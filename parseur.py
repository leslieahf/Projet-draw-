from tok import Lexer
from tok import Token
from difflib import get_close_matches
import re


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = {}  # Tracks declared variable
        self.function_table = {}  # Tracks declared functions
        self.current_context = None

    def parse(self):
        ast = []
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            
            if token.type == "FUNCTION_DECLARATION":
                ast.append(self.parse_function_declaration())
            elif token.type == "FUNCTION_CALL":
                ast.append(self.parse_function_call())
            elif token.type == "VARIABLE":
                ast.append(self.parse_assignment())
            elif token.type == "NUMBER":
                raise SyntaxError(f"Unexpected '{token.value}' at line {token.line}. Did you forget an assignment?")
            elif token.type == "DRAW_COMMAND" :
                ast.append(self.parse_draw_command())
            elif token.type == "PRINT":
                ast.append(self.parse_print())
            elif token.type == "IF":
                ast.append(self.parse_if())
            elif token.type == "RETURN":
                ast.append(self.parse_return())
            elif token.type == "WHILE":
                ast.append(self.parse_while())
            elif token.type == "FOR":
                ast.append(self.parse_for())
            else:
                raise SyntaxError(f"Unexpected {token.value} at line {token.line}")

        return ast

    def skip_whiteline(self):
        """Ignore whitespace and newline"""
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            if token.type in {"WHITESPACE", "NEWLINE"}:
                self.current_index += 1
            else:
                break  

    def skip_only_whitespace(self):
        """Only ignore whitespace"""
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            if token.type == "WHITESPACE":
                self.current_index += 1  
            else:
                break  

    def peek_next_token_type(self):
        if self.current_index + 1 < len(self.tokens):
            return self.tokens[self.current_index + 1].type
        return None

    def parse_return(self):
        """
        Parses a return statement like:
        return <expression>
        """
        token = self.tokens[self.current_index]
        if token.type != "RETURN":
            raise SyntaxError(f"Expected 'return', got {token.type} at line {token.line}")

        # Verify if `return` is within a function by checking preceding tokens
        is_inside_function = False
        for i in range(self.current_index - 1, -1, -1):
            prev_token = self.tokens[i]
            if prev_token.type == "FUNCTION_DECLARATION":
                # Check if an opening brace `{` follows the FUNCTION_DECLARATION
                if any(tok.type == "LBRACE" for tok in self.tokens[i + 1:self.current_index]):
                    is_inside_function = True
                    break

        if not is_inside_function:
            raise SyntaxError(f"Invalid 'return' statement at line {token.line}. Must be inside a function.")

        self.current_index += 1
        self.skip_whiteline()

        # Check if there's an expression after 'return'
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].type not in {"NEWLINE", "SEMICOLON", "RBRACE"}:
            expression = self.parse_expression(stop_at_newline=True)
        else:
            # No expression provided after return
            raise SyntaxError(
                f"Missing expression after 'return' at line {token.line}. Did you mean 'return 0'?"
            )

        # Determine the type based on the first token
        resolved_type = expression[0].type
        resolved_value = "".join(token.value for token in expression)

        # Check if the return value is a valid type
        valid_types = {"NUMBER", "STRING", "BOOLEAN", "VARIABLE"}
        if resolved_type not in valid_types:
            raise SyntaxError(
                f"Invalid type '{resolved_type}' for return value at line {token.line}. Expected one of: {', '.join(valid_types)}."
            )

        # Handle variable references
        if resolved_type == "VARIABLE":
            variable_name = expression[0].value
            if variable_name not in self.symbol_table:
                raise SyntaxError(
                    f"Variable '{variable_name}' used in return statement without being initialized at line {token.line}"
                )
            resolved_value = self.symbol_table[variable_name]["value"]
            resolved_type = self.symbol_table[variable_name]["type"]

        # Ensure the return value is a valid type
        if resolved_type not in {"NUMBER", "STRING", "BOOLEAN"}:
            raise SyntaxError(
                f"Invalid return type '{resolved_type}' at line {token.line}. Expected NUMBER, STRING, or BOOLEAN."
            )

        return {
            "type": "return",
            "value": resolved_value,
            "resolved_type": resolved_type,
        }


    def parse_assignment(self):
        token = self.tokens[self.current_index]
        variable_name = token.value  # Extract the variable name

        self.current_index += 1
        self.skip_only_whitespace()

        # Check for assignment operator `<-`
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "ASSIGN":
            raise SyntaxError(f"Expected '<-' after {variable_name} at line {token.line}")

        self.current_index += 1
        self.skip_only_whitespace()

        # Check for value after the assignment operator
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index] is None:
            raise SyntaxError(f"Expected value after '<-' at line {token.line}")

        # Parse the expression on the right-hand side
        expression = self.parse_expression(stop_at_newline=True)

        # Evaluate or validate the expression
        resolved_value = None
        resolved_type = None

        if len(expression) == 1:
            # Single-token expression (e.g., x <- 5 or x <- call h())
            resolved_token = expression[0]

            if isinstance(resolved_token, dict) and resolved_token["type"] == "function_call":
                # Handle function call result
                resolved_value = resolved_token["return_value"]
                resolved_type = resolved_token["return_type"]
            elif hasattr(resolved_token, "type"):
                # Regular token
                resolved_value = resolved_token.value
                resolved_type = resolved_token.type

                # Handle variable references
                if resolved_type == "VARIABLE":
                    if resolved_value not in self.symbol_table:
                        raise SyntaxError(f"Variable '{resolved_value}' used without being initialized at line {token.line}")
                    # Resolve variable type and value
                    resolved_value = self.symbol_table[resolved_value]["value"]
                    resolved_type = self.symbol_table[resolved_value]["type"]

                # Convert the resolved value to the appropriate type
                if resolved_type == "NUMBER" and isinstance(resolved_value, str):
                    try:
                        resolved_value = int(resolved_value)
                    except ValueError:
                        raise SyntaxError(f"Invalid value '{resolved_value}' for variable '{variable_name}' at line {token.line}. Expected a number.")

            else:
                raise SyntaxError(f"Unexpected token type in assignment at line {token.line}")

        else:
            # Complex expressions (e.g., x <- 5 + 3 or x <- call h() + 4)
            resolved_value = self.tokens_to_string(expression)
            first_token = expression[0]
            resolved_type = first_token.type if hasattr(first_token, "type") else "EXPRESSION"

        # Ensure valid types
        valid_types = {"NUMBER", "STRING", "BOOLEAN"}
        if resolved_type not in valid_types and resolved_type != "EXPRESSION":
            raise SyntaxError(f"Invalid type '{resolved_type}' for assignment at line {token.line}")

        # Update the symbol table with initialization status, type, and value
        self.symbol_table[variable_name] = {
            "initialized": True,
            "type": resolved_type,
            "value": resolved_value,
        }

        self.skip_whiteline()
        return {
            "type": "assignment",
            "variable": variable_name,
            "expression": self.tokens_to_string(expression),
        }

    def parse_expression(self, stop_at_newline=False):
        expression = []
        current_line = self.tokens[self.current_index].line

        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type not in {"NEWLINE", "RBRACE", "RPAREN", "SEMICOLON", "COMMA"}:
            if self.current_index >= len(self.tokens):
                break
            token = self.tokens[self.current_index]
            if stop_at_newline and token.line != current_line:
                break

            if token.type == "WHITESPACE":
                prev_token = expression[-1] if expression else None
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None
                if prev_token and next_token:
                    if prev_token.type in {"NUMBER", "VARIABLE", "STRING", "FUNCTION_CALL"} and next_token.type in {"FUNCTION_CALL", "VARIABLE", "STRING", "NUMBER"}:
                        raise SyntaxError(f"Expected operator between {prev_token.value} and {next_token.value} at line {token.line}")
                self.current_index += 1
                continue

            if token.type == "FUNCTION_CALL":
                # Parse the function call and add the result to the expression
                function_call_result = self.parse_function_call()
                # Wrap in a token-like structure
                expression.append(Token(
                    type=function_call_result["return_type"],
                    value=function_call_result["return_value"],
                    line=token.line,
                    column=token.column
                ))
                self.skip_whiteline()
                continue

            if token.type == "OPERATOR" or token.type == "COMPARAISON":
                prev_token = expression[-1] if expression else None
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None

                if prev_token is None or next_token is None:
                    if prev_token is None:
                        raise SyntaxError(f"Missing left operand at line {token.line}")
                    if next_token is None:
                        raise SyntaxError(f"Missing right operand at line {token.line}")

                if prev_token and next_token:
                    if prev_token.type == "STRING" or next_token.type == "STRING":
                        raise SyntaxError(f"Invalid comparison or operation with strings at line {token.line}")

                if token.value == "/":
                    # Skip any whitespace after the division operator
                    next_index = self.current_index + 1
                    while next_index < len(self.tokens) and self.tokens[next_index].type == "WHITESPACE":
                        next_index += 1

                    if next_index >= len(self.tokens):
                        raise SyntaxError(f"Invalid syntax: Missing operand after '/' at line {token.line}")

                    next_token = self.tokens[next_index]

                    # Handle division validation
                    if prev_token.type in {"NUMBER", "BOOLEAN", "FUNCTION_CALL", "VARIABLE"}:
                        # Handle previous token being a function call
                        if prev_token.type == "FUNCTION_CALL":
                            if "return_type" not in prev_token.value or prev_token.value["return_type"] != "NUMBER":
                                raise SyntaxError(f"Invalid operation! Function call does not return a valid numeric type at line {token.line}")

                        # Handle previous token being a variable
                        if prev_token.type == "VARIABLE":
                            if prev_token.value not in self.symbol_table:
                                raise SyntaxError(f"Variable '{prev_token.value}' used without being initialized at line {token.line}")
                            prev_value = self.symbol_table[prev_token.value]
                            if prev_value["type"] != "NUMBER":
                                raise SyntaxError(f"Invalid operation! Variable '{prev_token.value}' does not contain a numeric value at line {token.line}")

                        # Handle next token being a function call
                        if next_token.type == "FUNCTION_CALL":
                            if "return_type" not in next_token.value or next_token.value["return_type"] != "NUMBER":
                                raise SyntaxError(f"Invalid operation! Function call does not return a valid numeric type at line {token.line}")
                            if "return_value" in next_token.value and next_token.value["return_value"] == 0:
                                raise SyntaxError(f"Invalid operation! Division by 0 from function return at line {token.line}")

                        # Handle next token being a variable
                        if next_token.type == "VARIABLE":
                            if next_token.value not in self.symbol_table:
                                raise SyntaxError(f"Variable '{next_token.value}' used without being initialized at line {token.line}")
                            next_value = self.symbol_table[next_token.value]
                            if next_value["type"] != "NUMBER":
                                raise SyntaxError(f"Invalid operation! Variable '{next_token.value}' does not contain a numeric value at line {token.line}")
                            if next_value["value"] == 0:
                                raise SyntaxError(f"Invalid operation! Division by 0 using variable '{next_token.value}' at line {token.line}")

                        # Handle next token being a number
                        if next_token.type == "NUMBER" and next_token.value == "0":
                            raise SyntaxError(f"Invalid operation! Division by 0 at line {token.line}")
                    else:
                        raise SyntaxError(f"Invalid syntax: Missing or invalid operand for division at line {token.line}")

            if token.type == "COMPARAISON":
                valid_contexts = {"IF", "WHILE", "FOR", "ELIF"}
                if self.current_context not in valid_contexts:
                    raise SyntaxError(f"Invalid use of comparison operator outside allowed blocks (if, while, for, elif) at line {token.line}")
            expression.append(token)
            self.current_index += 1

        for token in expression:
            if token.type == "UNKNOWN":
                raise SyntaxError(f"Unexpected '{token.value}' at line {token.line}.")

        return expression


    

    def parse_print(self):
        token = self.tokens[self.current_index]
        if token.type != "PRINT":
            raise SyntaxError(f"Expected print, got {token.type} at line {token.line}")

        self.current_index += 1
        
        if self.current_index >= len(self.tokens)  or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after print at line {token.line}")

        self.skip_only_whitespace()
        expression = self.parse_expression()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after print expression at line {token.line}")
        
        # Validation des variables dans le print
        if len(expression) == 0 or all(tok.type == "WHITESPACE" for tok in expression):
            raise SyntaxError(f"Missing arguments in print expression at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()
        for tok in expression:
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")

        return {
            "type": "print",
            "expression": self.tokens_to_string(expression),
        }
    def parse_if(self):
        self.current_context = "IF"
        token = self.tokens[self.current_index]
        if token.type != "IF":
            raise SyntaxError(f"Expected if, got {token.type} at line {token.line}")

        self.current_index += 1

        # Vérifie la parenthèse ouvrante après le IF
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after if at line {token.line}")
        self.skip_only_whitespace()

        # Parse la condition entre les parenthèses
        condition = self.parse_expression()

        self.skip_only_whitespace()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after if condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()
        for tok in condition:
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")

        # Gérer les espaces et sauts de ligne avant le crochet ouvrant
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type in {"WHITESPACE", "NEWLINE"}:
            self.current_index += 1

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LBRACE":
            raise SyntaxError(f"Expected '{{' after if condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()

        # Parse le corps du bloc
        body = self.parse_block()
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RBRACE":
            raise SyntaxError(f"Expected '}}' after if condition at line {token.line}")
        self.current_index +=1
        self.skip_whiteline()

        self.current_context = None
        return {"type": "if", "condition": self.tokens_to_string(condition), "body": body}

    def parse_for_expression(self):
        """
        Parse the expressions specific to a for loop, including initialization, condition, and increment.
        Handles cases like `for(;;)` where expressions are empty.
        Returns a dictionary with parsed parts of the for loop.
        """
        init, condition, increment = None, None, None

        # Parse initialization
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "SEMICOLON":
            init = self.parse_expression(stop_at_newline=False)
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "SEMICOLON":
            raise SyntaxError(f"Expected ';' after initialization at line {self.tokens[self.current_index - 1].line}")
        self.current_index += 1  # Skip ';'

        # Parse condition
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "SEMICOLON":
            condition = self.parse_expression(stop_at_newline=False)
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "SEMICOLON":
            raise SyntaxError(f"Expected ';' after condition at line {self.tokens[self.current_index - 1].line}")
        self.current_index += 1  # Skip ';'

        # Parse increment
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RPAREN":
            increment = self.parse_expression(stop_at_newline=False)
        self.skip_only_whitespace()

        return {
            "initialization": self.tokens_to_string(init) if init else None,
            "condition": self.tokens_to_string(condition) if condition else None,
            "increment": self.tokens_to_string(increment) if increment else None,
        }

    def parse_block(self):
        ast = []
        while self.current_index < len(self.tokens) :
            self.skip_whiteline()
            if self.current_index >= len(self.tokens):
                break
            token = self.tokens[self.current_index]
            if token.type == "FUNCTION_DECLARATION":
                ast.append(self.parse_function_declaration())
            elif token.type == "FUNCTION_CALL":
                ast.append(self.parse_function_call())
            elif token.type == "VARIABLE":
                ast.append(self.parse_assignment())
            elif token.type == "NUMBER":
                raise SyntaxError(f"Unexpected '{token.value}' at line {token.line}. Did you forget an assignment?")
            elif token.type == "DRAW_COMMAND" :
                ast.append(self.parse_draw_command())
            elif token.type == "PRINT":
                ast.append(self.parse_print())
            elif token.type == "IF":
                ast.append(self.parse_if())
            elif token.type == "RETURN":
                ast.append(self.parse_return())
            elif token.type == "WHILE":
                ast.append(self.parse_while())
            elif token.type == "RBRACE":
                break
            elif token.type == "FOR":
                ast.append(self.parse_for())
            else:
                raise SyntaxError(f"Unexpected {token.value} at line {token.line}")

        return ast
    
    def parse_for(self):
        self.current_context = "FOR"
        token = self.tokens[self.current_index]
        if token.type != "FOR":
            raise SyntaxError(f"Expected for, got {token.type} at line {token.line}")
        self.current_index += 1
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after for at line {token.line}")
        
        for_parts = self.parse_for_expression()

        self.skip_only_whitespace()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after for  at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LBRACE":
            raise SyntaxError(f"Expected '{{' after for at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()

        body = self.parse_block()
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RBRACE":
            raise SyntaxError(f"Expected '}}' after for at line {token.line}")
        self.current_index +=1
        self.skip_whiteline()
        
        self.current_context = None
        return {
            "type": "for",
            "initialization": for_parts["initialization"],
            "condition": for_parts["condition"],
            "increment": for_parts["increment"],
            "body": body,
        }
    
    def parse_while(self):
        self.current_context = "WHILE"
        token = self.tokens[self.current_index]
        if token.type != "WHILE":
            raise SyntaxError(f"Expected WHILE, got {token.type} at line {token.line}")

        self.current_index += 1

    
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after while at line {token.line}")
        self.skip_only_whitespace()

        # Parsing of the condition
        condition = self.parse_expression()

        self.skip_only_whitespace()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after while condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()
        for tok in condition:
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")
    
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LBRACE":
            raise SyntaxError(f"Expected '{{' after while condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()

      
        # Parse le corps du bloc
        body = self.parse_block()
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RBRACE":
            raise SyntaxError(f"Expected '}}' after while at line {token.line}")
        self.current_index +=1
        self.skip_whiteline()
        self.current_context = None
        return {"type": "while", "condition": self.tokens_to_string(condition), "body": body}

    def parse_draw_command(self):
        token = self.tokens[self.current_index]
        if token.type != "DRAW_COMMAND":
            raise SyntaxError(f"Expected DRAW_COMMAND, got {token.type} at line {token.line}")

        command_name = token.value
        self.current_index += 1
        self.skip_only_whitespace()

        # Check for opening parenthesis
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after {command_name} at line {token.line}")

        self.current_index += 1
        self.skip_only_whitespace()

        args = []
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RPAREN":
            current_token = self.tokens[self.current_index]

            # Validate and parse arguments
            if current_token.type in {"STRING", "VARIABLE", "NUMBER"}:
                args.append(current_token.value)
            elif self.current_index < len(self.tokens) and self.tokens[self.current_index].type == "COMMA":
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None
                if not next_token or next_token.type in {"RPAREN", "COMMA"}:
                    raise SyntaxError(f"Unexpected ',' at line {self.tokens[self.current_index].line}. Parameter expected after ','.")
            else:
                raise SyntaxError(f"Invalid argument '{current_token.value}' at line {current_token.line}")

            self.current_index += 1
            self.skip_only_whitespace()

        # Check for closing parenthesis
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' to close arguments for {command_name} at line {token.line}")

        self.current_index += 1  # Skip RPAREN
        self.skip_whiteline()

        if command_name == "draw":
            # Specify number of arguments excepted 
            expected_shapes = {
                "carre": 4,       
                "rectangle": 5,   
                "triangle": 3,   
                "cercle": 4,      
                "line": 3,        
                "losange": 5,     
                "polygon": 5,  
                "trapeze": 6    
            }

            shape = args[0]
            if shape not in expected_shapes:
                raise SyntaxError(f"Invalid shape '{shape}' for 'draw' at line {token.line}. Expected one of {', '.join(expected_shapes.keys())}.")

            # Check that RGB is valid
            rgb = args[1]
            try:
                if "," in rgb:
                    # Case: RGB is a string like "255,0,128"
                    rgb_values = list(map(int, rgb.replace("\"", "").split(",")))
                elif rgb in self.symbol_table:
                    # Case: RGB is a variable
                    rgb_value = self.symbol_table[rgb]["value"]
                    if not isinstance(rgb_value, str) or "," not in rgb_value:
                        raise SyntaxError(f"Variable '{rgb}' must contain a string in 'R,G,B' format at line {token.line}.")
                    rgb_values = list(map(int, rgb_value.split(",")))
                else:
                    raise SyntaxError(f"Invalid RGB argument '{rgb}' at line {token.line}. Expected 'R,G,B' or an initialized variable.")

                # Validate the RGB values
                if len(rgb_values) != 3 or any(value < 0 or value > 255 for value in rgb_values):
                    raise SyntaxError(f"Invalid RGB values '{rgb}' at line {token.line}. Expected format: 'R,G,B' with values between 0 and 255.")
            except ValueError:
                raise SyntaxError(f"RGB values must be integers at line {token.line}.")
            
            if not (shape == "line" or shape == "triangle"):
                arg = args[2]  # Directly access the third argument
                if isinstance(arg, str) and "," in arg:
                    coords = arg.replace("\"", "").split(",")
                    if len(coords) != 2:
                        raise SyntaxError(f"Invalid coordinates format '{arg}' at line {token.line}. Expected format: 'X1,Y1'.")
                    if not all(coord.strip().isdigit() for coord in coords):
                        raise SyntaxError(f"Invalid coordinate format '{arg}' at line {token.line}. Expected numbers separated by commas.")
                elif arg in self.symbol_table:
                    value = self.symbol_table[arg]["value"]
                    if not isinstance(value, (int, float)):
                        raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Must be a valid number or initialized variable.")
                else:
                    raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Must be a valid coordinate or initialized variable.")

            if shape == "line":
                arg = args[2]  # Directly access the third argument (coordinates)
                if isinstance(arg, str) and "," in arg:
                    # Case: Argument is a coordinate string
                    coords = [coord.strip() for coord in arg.replace("\"", "").split(",")]
                    if len(coords) != 4:
                        raise SyntaxError(f"Invalid coordinates format '{arg}' at line {token.line}. Expected format: 'X1,Y1,X2,Y2'.")
                    if not all(coord.isdigit() for coord in coords):
                        raise SyntaxError(f"Coordinates must be positive integers in '{arg}' at line {token.line}.")
                    coords = list(map(int, coords))  # Convert to integers for further validation
                    if any(value < 0 for value in coords):
                        raise SyntaxError(f"Coordinate values must be >= 0 in '{arg}' at line {token.line}.")
                elif arg in self.symbol_table:
                    # Case: Argument is a variable
                    value = self.symbol_table[arg]["value"]
                    if not isinstance(value, str) or "," not in value:
                        raise SyntaxError(f"Variable '{arg}' must contain a string of coordinates in 'X1,Y1,X2,Y2' format at line {token.line}.")
                    coords = [coord.strip() for coord in value.split(",")]
                    if len(coords) != 4 or not all(coord.isdigit() for coord in coords):
                        raise SyntaxError(f"Invalid coordinate format in variable '{arg}' at line {token.line}.")
                    coords = list(map(int, coords))  # Convert to integers for validation
                    if any(value < 0 for value in coords):
                        raise SyntaxError(f"Coordinate values must be >= 0 in variable '{arg}' at line {token.line}.")
                else:
                    # Invalid argument case
                    raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Must be a valid coordinate string or initialized variable.")

            if shape == "triangle":
                arg = args[2]  # Directly access the fourth argument (coordinates)
                if isinstance(arg, str) and "," in arg:
                    # Case: Argument is a coordinate string
                    coords = [coord.strip() for coord in arg.replace("\"", "").split(",")]
                    if len(coords) != 6:
                        raise SyntaxError(f"Invalid coordinates format '{arg}' at line {token.line}. Expected format: 'X1,Y1, X2,Y2, X3,Y3'.")
                    if not all(coord.isdigit() for coord in coords):
                        raise SyntaxError(f"Coordinates must be positive integers in '{arg}' at line {token.line}.")
                    coords = list(map(int, coords))  # Convert to integers for further validation
                    if any(value < 0 for value in coords):
                        raise SyntaxError(f"Coordinate values must be >= 0 in '{arg}' at line {token.line}.")
                elif arg in self.symbol_table:
                    # Case: Argument is a variable
                    value = self.symbol_table[arg]["value"]
                    if not isinstance(value, str) or "," not in value:
                        raise SyntaxError(f"Variable '{arg}' must contain a string of coordinates in 'X1,Y1, X2,Y2, X3,Y3' format at line {token.line}.")
                    coords = [coord.strip() for coord in value.split(",")]
                    if len(coords) != 4 or not all(coord.isdigit() for coord in coords):
                        raise SyntaxError(f"Invalid coordinate format in variable '{arg}' at line {token.line}.")
                    coords = list(map(int, coords))  # Convert to integers for validation
                    if any(value < 0 for value in coords):
                        raise SyntaxError(f"Coordinate values must be >= 0 in variable '{arg}' at line {token.line}.")
                else:
                    # Invalid argument case
                    raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Must be a valid coordinate string or initialized variable.")
                
            if (shape != "line" and shape != "triangle"):
                for i, arg in enumerate(args[3:], start=3): 
                    if arg in self.symbol_table:
                        # Cas : Variable
                        print("Symbol Table:", self.symbol_table)
                        value = self.symbol_table[arg]["value"]
                        if not isinstance(value, int):
                            raise SyntaxError(f"Invalid value '{value}' for variable '{arg}' at line {token.line}. Expected an integer.")
                    elif arg.isdigit():
                        # Cas : Nombre direct
                        int_value = int(arg)
                        if int_value <= 0:
                            raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Values must be > 0.")
                    else:
                        # Cas : Argument invalide
                        raise SyntaxError(f"Invalid argument '{arg}' at line {token.line}. Expected an integer or initialized variable.")
            
            # Validate remaining arguments
            expected_arg_count = expected_shapes[shape]
            if expected_arg_count is not None and len(args) != expected_arg_count:
                raise SyntaxError(f"Invalid number of arguments for shape '{shape}' at line {token.line}. Expected {expected_arg_count}, got {len(args)}.")
            
                
        elif command_name == "freedraw":
            if args:
                raise SyntaxError(f"'freedraw' does not accept any arguments at line {token.line}")

        return {
            "type": "draw_command",
            "command": command_name,
            "args": args,
        }



    def parse_function_call(self):
        """
        Parses a function call like:
        call myFunction(5, "Hello")
        """
        token = self.tokens[self.current_index]
        if token.type != "FUNCTION_CALL":
            raise SyntaxError(f"Expected a function call, got {token.type} at line {token.line}")

        self.current_index += 1
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "VARIABLE":
            raise SyntaxError(f"Invalid function name at line {token.line}")

        t = self.tokens[self.current_index]
        function_name = t.value
        self.current_index += 1
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after function name at line {token.line}")
        self.current_index += 1
        self.skip_only_whitespace()

        # Parse arguments
        arguments = []
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RPAREN":
            arg_token = self.tokens[self.current_index]
            if arg_token.type in {"VARIABLE", "NUMBER", "STRING"}:
                if arg_token.type == "VARIABLE":
                    # Resolve variable type and value from symbol table
                    if arg_token.value not in self.symbol_table:
                        raise SyntaxError(f"Variable '{arg_token.value}' used without being initialized at line {arg_token.line}")
                    resolved_type = self.symbol_table[arg_token.value]["type"]
                    resolved_value = self.symbol_table[arg_token.value]["value"]
                    arguments.append((resolved_value, resolved_type))
                else:
                    # Directly add non-variable arguments
                    arguments.append((arg_token.value, arg_token.type))
            elif arg_token.type == "COMMA":
                pass  # Allow commas between arguments
            else:
                raise SyntaxError(f"Invalid argument syntax at line {arg_token.line}")
            self.current_index += 1
            self.skip_only_whitespace()

        # Ensure closing parenthesis
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' to close argument list at line {token.line}")
        self.current_index += 1  # Skip RPAREN

        # Validate function existence
        if function_name not in self.function_table:
            raise SyntaxError(f"Undefined function '{function_name}' at line {token.line}")

        # Validate argument count and types
        declared_func = self.function_table[function_name]
        if len(arguments) != len(declared_func["parameters"]):
            raise SyntaxError(
                f"Function '{function_name}' expects {len(declared_func['parameters'])} arguments but got {len(arguments)} at line {token.line}"
            )

        for (arg_value, arg_type), (param_name, param_type) in zip(arguments, declared_func["parameters"]):
            # Map declared parameter type (param_type) to the expected token type
            type_map = {
                "int": "NUMBER",
                "str": "STRING",
                "bool": "BOOLEAN",
                "float": "NUMBER"
            }
            expected_type = type_map.get(param_type)
            if expected_type is None:
                raise SyntaxError(
                    f"Invalid parameter type '{param_type}' in function '{function_name}'. Allowed types are: {', '.join(type_map.keys())}."
                )
            # Compare the expected type with the actual argument type
            if expected_type != arg_type:
                raise SyntaxError(
                    f"Type mismatch for parameter '{param_name}' in function '{function_name}' at line {token.line}: "
                    f"expected {param_type}, got {arg_type} (value: {arg_value})"
                )

        # Get the return value from the function
        function_body = declared_func.get("body", [])
        return_stmt = next((stmt for stmt in function_body if stmt["type"] == "return"), None)

        if return_stmt is None or "value" not in return_stmt:
            raise SyntaxError(f"Function '{function_name}' does not return a value.")

        return_value = return_stmt["value"]
        return_type = return_stmt["resolved_type"]

        return {
            "type": "function_call",
            "name": function_name,
            "arguments": arguments,
            "return_value": return_value,
            "return_type": return_type,
        }

    def parse_function_parameters(self):
        """
        Parses the parameter list of a function declaration, e.g., (int x, string y).
        Returns a list of tuples with parameter names and types.
        """
        parameters = []
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RPAREN":
            type_token = self.tokens[self.current_index]
            if type_token.type != "VARIABLE_DEF":
                raise SyntaxError(f"Expected type (e.g., 'int', 'str', 'bool'), got '{type_token.value}' at line {type_token.line}")
            param_type = type_token.value
            self.current_index += 1

            if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "WHITESPACE":
                raise SyntaxError(f"Missing argument after {type_token.value} at line {type_token.line}")
        
            self.skip_only_whitespace()

            if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "VARIABLE":
                raise SyntaxError(f"Incorrect statement after {type_token.value} at line {type_token.line}")
        
            param_name_token = self.tokens[self.current_index]
            parameters.append((param_name_token.value, param_type))
            self.current_index += 1
            self.skip_only_whitespace()

            # Handle commas
            if self.current_index < len(self.tokens) and self.tokens[self.current_index].type == "COMMA":
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None
                if next_token.type == "RPAREN" or next_token.type == "COMMA":
                    raise SyntaxError(f"Unexpected ',' at line {self.tokens[self.current_index].line}. Parameter expected after ','.")

                self.current_index += 1
                self.skip_only_whitespace()
    
        return parameters


    def parse_function_declaration(self):
        self.current_context = "FUNCTION_DECLARATION"
        local_symbol_table = {}  # Local scope for this function
        global_symbol_table_backup = self.symbol_table  # Backup global scope
        self.symbol_table = local_symbol_table  # Use local scope

        token = self.tokens[self.current_index]
        if token.type != "FUNCTION_DECLARATION":
            raise SyntaxError(f"Expected 'func', got {token.type} at line {token.line}")

        self.current_index += 1
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "VARIABLE":
            raise SyntaxError(f"Invalid function name at line {token.line}")

        func_name = self.tokens[self.current_index].value
        self.current_index += 1
        self.skip_only_whitespace()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after function name at line {token.line}")
        self.current_index += 1
        self.skip_only_whitespace()

        # Parse parameters
        parameters = self.parse_function_parameters()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after parameters at line {token.line}")
        self.current_index += 1
        self.skip_whiteline()

        # Initialize parameters in local symbol table
        for param_name, param_type in parameters:
            local_symbol_table[param_name] = {
                "initialized": True,
                "type": param_type,
                "value": None,  # Parameters have no initial value unless explicitly set
            }

        # Parse function body
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LBRACE":
            raise SyntaxError(f"Expected '{{' to start function body at line {token.line}")
        self.current_index += 1
        self.skip_whiteline()

        body = self.parse_block()
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RBRACE":
            raise SyntaxError(f"Expected '}}' after {func_name} declaration at line {token.line}")
        self.current_index += 1
        self.skip_whiteline()

        # Validate return statement presence
        found_return = any(statement.get("type") == "return" for statement in body)
        if not found_return:
            raise SyntaxError(f"Missing 'return' statement in function '{func_name}' at line {token.line}")

        # Restore global symbol table after parsing
        self.symbol_table = global_symbol_table_backup
        self.current_context = None

        # Store the function in the function table
        self.function_table[func_name] = {
            "parameters": parameters,
            "body": body,
        }

        return {
            "type": "function_declaration",
            "name": func_name,
            "parameters": parameters,
            "body": body,
        }



    def tokens_to_string(self, tokens):
        try:
            return " ".join(token.value for token in tokens)
        except Exception as e:
            print(f"Error converting tokens to string: {e}")
            raise
        
            