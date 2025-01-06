from tok import Lexer
from difflib import get_close_matches
import re
class GrammarAnalyzer:
    def __init__(self):
        self.valid_tokens = {
            "print()": ["prin()", "prit()", "printf()"],
            "=": ["<-"],
            "==": ["eq"],
            ">": ["sup", "sups"],
            ">=": ["sup", "sups"],
            "<": ["inf", "infs"],
            "<=": ["inf", "infs"],
        }

    def analyse(self, token_value):
        suggestions = []
        for valid_token, alternatives in self.valid_tokens.items():
            all_alternatives = [valid_token] + alternatives
            matches = get_close_matches(token_value, all_alternatives, n=1, cutoff=0.6)
            if matches:
                suggestions.append(f"Did you mean '{matches[0]}' instead of '{token_value}'?")
        if suggestions:
            return suggestions
        else:
            return [f"No suggestion found for '{token_value}'."]

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.symbol_table = {}  # Tracks declared variable
        self.function_table = {}  # Tracks declared functions
        self.analyzer = GrammarAnalyzer()  # Instance de l’analyzer
        self.current_context = None

    def parse(self):
        ast = []
        print(f"DEBUG: Nombre total de tokens : {len(self.tokens)}")
        print("DEBUG: Tokens :", self.tokens)
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            print(f"DEBUG: Token actuel : {token}")
            
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
                print(f"l'index actuelle est {self.current_index}")
                print(f"DEBUG: Reached else block with token: {token}")
                raise SyntaxError(f"Unexpected {token.value} at line {token.line}")

        return ast

    def skip_whiteline(self):
        """Ignore uniquement les espaces ou sauts de ligne présents."""
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            if token.type in {"WHITESPACE", "NEWLINE"}:
                self.current_index += 1
            else:
                break  

    def skip_only_whitespace(self):
        """Ignore uniquement les espaces."""
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

        valid_contexts = {"FUNCTION_DECLARATION"}
        if self.current_context not in valid_contexts :
            raise SyntaxError(f"Invalid 'return' statement at {token.line}")
        self.current_index += 1  # Skip the 'return' keyword
        self.skip_whiteline()

        # Check if there's an expression after 'return'
        if self.current_index < len(self.tokens) and self.tokens[self.current_index].type not in {"NEWLINE", "SEMICOLON", "RBRACE"}:
            expression = self.parse_expression(stop_at_newline=True)
        else:
            # No expression provided after 'return'
            expression = None

        return {
            "type": "return",
            "expression": self.tokens_to_string(expression) if expression else None,
        }

    def parse_assignment(self):
        token = self.tokens[self.current_index]
        variable_name = token.value
        
        self.current_index += 1
        self.skip_only_whitespace()

        if  self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "ASSIGN":
            raise SyntaxError(f"Expected '<-' after {variable_name} at line {token.line}")
        
        self.current_index += 1
        self.skip_only_whitespace()


        if self.current_index >= len(self.tokens) or self.tokens[self.current_index] is None :
            raise SyntaxError(f"Expected value after VARIABLE at line {token.line}")
        
        expression = self.parse_expression(stop_at_newline=True)
        # Validation des variables utilisées dans l'expression
        for tok in expression:
            if tok.type == "VARIABLE" and tok.value == variable_name:
                # Vérifie si la variable est référencée dans sa propre affectation sans être initialisée auparavant
                if variable_name not in self.symbol_table:
                    raise SyntaxError(f"{variable_name}' used in its own initialization before being initialized at line {tok.line}")
                
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                    raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")
        
        self.symbol_table[variable_name] = True  # Marque la variable comme initialisée
        self.skip_whiteline()
        return {
            "type": "assignment",
            "variable": variable_name,
            "expression": self.tokens_to_string(expression),
        }
    
    def parse_expression(self, stop_at_newline=False):
        expression = []
        current_line = self.tokens[self.current_index].line
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type not in {"NEWLINE", "RBRACE", "RPAREN", "SEMICOLON", "COMMA"} :
            if self.current_index >= len(self.tokens):
                break
            token = self.tokens[self.current_index]
            if stop_at_newline and token.line != current_line:
                break
            
            if token.type == "WHITESPACE":
                prev_token = expression[-1] if expression else None
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None
                if prev_token and next_token:
                    if prev_token.type in {"NUMBER", "VARIABLE", "STRING","FUNCTION_CALL"} and next_token.type in {"FUNCTION_CALL", "VARIABLE", "STRING","NUMBER"}:
                        raise SyntaxError(f"Expected operator between {prev_token.value} and {next_token.value} at line {token.line}")
                self.current_index += 1
                continue

            # Validation : pas d'opérations entre types incompatibles
            if token.type == "OPERATOR" or token.type == "COMPARAISON":
                prev_token = expression[-1] if expression else None
                next_token = self.tokens[self.current_index + 1] if self.current_index + 1 < len(self.tokens) else None

                if (prev_token is None or next_token is None):
                    if prev_token is None :
                        raise SyntaxError(f"Missing left operand at line {token.line}")
                    if next_token is None :
                        raise SyntaxError(f"Missing right operand at line {token.line}")
                    
                if prev_token and next_token:
                    # Trouver le token précédent en ignorant les espaces
                    prev_index = self.current_index - 1
                    while prev_index >= 0 and self.tokens[prev_index].type == "WHITESPACE":
                        prev_index -= 1
                    prev_token = self.tokens[prev_index] if prev_index >= 0 else None

                    # Trouver le token suivant en ignorant les espaces
                    next_index = self.current_index + 1
                    while next_index < len(self.tokens) and self.tokens[next_index].type == "WHITESPACE":
                        next_index += 1
                    next_token = self.tokens[next_index] if next_index < len(self.tokens) else None

                    if prev_token.type == "STRING" :
                        raise SyntaxError(f"Invalid comparison or operation with strings at line {token.line}")
                    if next_token.type == "STRING":
                        raise SyntaxError(f"Invalid comparison or operation with strings at line {token.line}")
                    
                if token.value == "/":
                    # Trouver le token précédent en ignorant les espaces
                    prev_index = self.current_index - 1
                    while prev_index >= 0 and self.tokens[prev_index].type == "WHITESPACE":
                        prev_index -= 1
                    prev_token = self.tokens[prev_index] if prev_index >= 0 else None

                    # Trouver le token suivant en ignorant les espaces
                    next_index = self.current_index + 1
                    while next_index < len(self.tokens) and self.tokens[next_index].type == "WHITESPACE":
                        next_index += 1
                    next_token = self.tokens[next_index] if next_index < len(self.tokens) else None
                    # Vérification des opérandes autour de "/"
                    if prev_token and next_token:
                        if prev_token.type == "NUMBER" and next_token.type == "NUMBER" and next_token.value == "0":
                            raise SyntaxError(f"Invalid operation! Division by 0 at line {token.line}")
                    else:
                        raise SyntaxError(f"Invalid syntax: Missing operand for division at line {token.line}")
                    
            if token.type == "COMPARAISON":      
                valid_contexts = {"IF", "WHILE", "FOR", "ELIF"}  # Contextes autorisés pour une comparaison
                if self.current_context not in valid_contexts:
                    raise SyntaxError(f"Invalid use of comparison operator outside allowed blocks (if, while, for, elif) at line {token.line}")
            expression.append(token)
            self.current_index += 1
        """
        for token in expression :
            if token.type not in TOKEN_SPECIFICATIONS :
                raise SyntaxError(f"Unexpected {token.value} at {token.line}")
        """
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
        # Parse le corps du bloc
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

        # Vérifie la parenthèse ouvrante après le WHILE
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after while at line {token.line}")
        self.skip_only_whitespace()

        # Parse la condition entre les parenthèses
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

        self.current_index += 1
        args = []

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after DRAW_COMMAND at line {token.line}")

        self.current_index += 1
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RPAREN":
            args.append(self.tokens[self.current_index])
            self.current_index += 1

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after DRAW_COMMAND arguments at line {token.line}")

        self.current_index += 1  # Skip RPAREN
        return {"type": "draw_command", "command": token.value, "args": self.tokens_to_string(args)}


    def parse_function_call(self):
        """
        Parses a function call like:
        myFunction(5, "Hello")
        """

        token = self.tokens[self.current_index]
        if token.type != "FUNCTION_CALL":
            raise SyntaxError(f"Expected a function call, got {token.type} at line {token.line}")
    
        self.current_index += 1
        self.skip_only_whitespace()
        
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "VARIABLE":
            raise SyntaxError(f"Invalid function name at line {token.line}")

        t = self.tokens[self.current_index]
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
                arguments.append((arg_token.value, arg_token.type))
            elif arg_token.type == "COMMA":
                pass  # Allow commas between arguments
            else:
                raise SyntaxError(f"Invalid argument syntax at line {arg_token.line}")
            self.current_index += 1

        # Ensure closing parenthesis
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' to close argument list at line {token.line}")
        self.current_index += 1  # Skip RPAREN

        function_name = t.value
        if function_name not in self.function_table:
            raise SyntaxError(f"Undefined function '{function_name}' at line {token.line}")
            
        # Validate argument count and types
        declared_func = self.function_table[function_name]
        if len(arguments) != len(declared_func["parameters"]):
            raise SyntaxError(f"Function '{function_name}' expects {len(declared_func['parameters'])} arguments but got {len(arguments)} at line {token.line}")
    
        for (arg_value, arg_type), (param_name, param_type) in zip(arguments, declared_func["parameters"]):
            if param_type != arg_type:
                raise SyntaxError(f"Type mismatch for parameter '{param_name}' in function '{function_name}' at line {token.line}: expected {param_type}, got {arg_type}")
    
        return {
            "type": "function_call",
            "name": function_name,
            "arguments": arguments,
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

        # Parse parameters using the new function
        parameters = self.parse_function_parameters()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after parameters at line {token.line}")
    
        self.current_index += 1 
        self.skip_whiteline()

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

        found_return = any(statement.get("type") == "return" for statement in body)
        if not found_return:
            raise SyntaxError(f"Missing 'return' statement in function '{func_name}' at line {token.line}")
    
        self.current_context = None

        # Store the function in the function table
        self.function_table[func_name] = {
            "parameters": parameters,
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
        
            