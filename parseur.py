from tok import Lexer
from difflib import get_close_matches

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
        self.symbol_table = {}  # Stocke les variables initialisées
        self.analyzer = GrammarAnalyzer()  # Instance de l’analyzer
        self.current_context = None

    def parse(self):
        ast = []
        print(f"DEBUG: Nombre total de tokens : {len(self.tokens)}")
        print("DEBUG: Tokens :", self.tokens)
        while self.current_index < len(self.tokens):
            self.skip_whiteline()
            if self.current_index >= len(self.tokens):
                break
            token = self.tokens[self.current_index]
            print(f"DEBUG: Token actuel : {token}")
            """
            #Vérification des tokens inconnus
            if token.type not in {"VARIABLE", "NUMBER", "PRINT", "IF", "WHILE", "FOR", "OPERATOR", "COMPARAISON", "DRAW_COMMAND", "ASSIGN", "LPAREN", "RPAREN", "LBRACE", "RBRACE"}:
                suggestions = self.analyzer.analyse(token.value)
                raise SyntaxError(f"Unknown token '{token.value}' at line {token.line}. Suggestions: {', '.join(suggestions)}")
            """
            if token.type == "VARIABLE":
                ast.append(self.parse_assignment())
            elif token.type == "NUMBER":
                raise SyntaxError(f"Unexpected '{token.value}' at line {token.line}. Did you forget an assignment?")
            elif token.type == "PRINT":
                ast.append(self.parse_print())
            elif token.type == "IF":
                ast.append(self.parse_if())
            elif token.type == "WHILE":
                ast.append(self.parse_while())
            elif token.type == "FOR":
                ast.append(self.parse_for())
            else:
                raise SyntaxError(f"Unexpected {token.value} at line {token.line}")

        return ast

    def skip_whiteline(self):
        """Ignore uniquement les espaces ou sauts de ligne présents."""
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            if token.type in {"WHITESPACE", "NEWLINE"}:
                self.current_index += 1  # Ignore les espaces et ou les sauts de lignes et avance
            else:
                break  # S'arrête dès qu'un token non espace ou saut de ligne est rencontré

    def skip_only_whitespace(self):
        """Ignore uniquement les espaces."""
        while self.current_index < len(self.tokens):
            token = self.tokens[self.current_index]
            if token.type in {"WHITESPACE"}:
                self.current_index += 1  # Ignore les espaces et avance
            else:
                break  # S'arrête dès qu'un token non espace est rencontré

    def peek_next_token_type(self):
        if self.current_index + 1 < len(self.tokens):
            return self.tokens[self.current_index + 1].type
        return None

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
                    if prev_token.type in {"NUMBER", "VARIABLE", "STRING"} and next_token.type in {"NUMBER", "VARIABLE", "STRING"}:
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

        for tok in expression:
            k = 0
            if tok.type == "WHITESPACE":
                k += 1
                tok += 1

        if k == len(expression):
             raise SyntaxError(f"Missing arguments in print expression at line {token.line}")

        self.current_index += 1

        # Validation des variables dans le print
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
        body = self.parse()

        self.current_context = None
        return {"type": "if", "condition": self.tokens_to_string(condition), "body": body}

    def parse_for_expression(self):
        """
        Parse the expressions specific to a for loop, including initialization, condition, and increment.
        Returns a dictionary with parsed parts of the for loop.
        """
        init = self.parse_expression(stop_at_newline=False)
        print(self.current_index)        
        self.skip_only_whitespace()
            
        if self.current_index  >= len(self.tokens) or self.tokens[self.current_index].type != "SEMICOLON":
            raise SyntaxError(f"Expected ';' after initialization at line {self.tokens[self.current_index].line}")
        self.current_index += 1

        condition = self.parse_expression(stop_at_newline=False)

        self.skip_only_whitespace()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "SEMICOLON":
            raise SyntaxError(f"Expected ';' after condition at line {self.tokens[self.current_index].line}")
        self.current_index += 1

        for tok in condition:
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")
        for tok in init:
            if tok.type == "VARIABLE" and tok.value not in self.symbol_table:
                raise SyntaxError(f"'{tok.value}' used without being initialized at line {tok.line}")
            
        increment = self.parse_expression(stop_at_newline=False)
        self.skip_only_whitespace()
        return {
            "initialization": self.tokens_to_string(init),
            "condition": self.tokens_to_string(condition),
            "increment": self.tokens_to_string(increment),
        }

    def parse_for(self):
        self.current_context = "FOR"
        token = self.tokens[self.current_index]
        if token.type != "FOR":
            raise SyntaxError(f"Expected for, got {token.type} at line {token.line}")
        self.current_index += 1
        self.skip_whiteline()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LPAREN":
            raise SyntaxError(f"Expected '(' after for at line {token.line}")
        
        print(self.current_index)        
        for_parts = self.parse_for_expression()

        self.skip_only_whitespace()
        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RPAREN":
            raise SyntaxError(f"Expected ')' after for condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "LBRACE":
            raise SyntaxError(f"Expected '{{' after for condition at line {token.line}")

        self.current_index += 1
        self.skip_whiteline()
        # Parse le corps du bloc
        body = self.parse()
        
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
        body = []
        while self.current_index < len(self.tokens) and self.tokens[self.current_index].type != "RBRACE":
            body.append(self.parse())
            self.skip_whiteline()

        if self.current_index >= len(self.tokens) or self.tokens[self.current_index].type != "RBRACE":
            raise SyntaxError(f"Expected '}}' after while condition at line {token.line}")
        self.current_index +=1
        self.skip_whiteline()

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


    def tokens_to_string(self, tokens):
        try:
            return " ".join(token.value for token in tokens)
        except Exception as e:
            print(f"Error converting tokens to string: {e}")
            raise
        
            