import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, line={self.line}, column={self.column})"

class Lexer:
    TOKEN_SPECIFICATIONS = [
        ("WHITESPACE", r"[ \t]+"),
        ("NEWLINE", r"\n"),
        ("PRINT", r"print"),
        ("IF", r"if"),
        ("ELSE", r"else"),
        ("ELIF", r"elif"),
        ("BREAK", r"break"),
        ("WHILE", r"while"),
        ("FOR", r"for"),
        ("SEMICOLON", r";"),
        ("COMMA", r","),
        ("WIN", r"window"),
        ("FUNCTION_DECLARATION", r"func"),
        ("RETURN", r"return"),
        ("VARIABLE_DEF", r"(int|float|str|bool)"),  
        ("FUNCTION_CALL", r"call"),
        ("BOOLEAN", r"(true|false)"),
        ("DRAW_COMMAND", r"draw|freedraw"),
        ("NUMBER", r"\d+(\.\d+)?"),
        ("STRING", r'"[^"]*"|\'[^\']*\''),
        ("COMPARAISON", r"(eq|neq|sup|inf|infs|sups)"), 
        ("VARIABLE", r"[a-zA-Z][a-zA-Z0-9]*"),
        ("ASSIGN", r"<-"),
        ("OPERATOR", r"[-+*/]"), 
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("HELP", r"help"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("UNKNOWN", r".+"),
    ]

    def __init__(self, code):
        if not code.strip():
            raise ValueError("Code source vide. Assurez-vous d'avoir fourni un code.")
        self.code = code
        self.tokens = []

    def tokenize(self):
        regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.TOKEN_SPECIFICATIONS)
        line_num = 1
        line_start = 0

        for match in re.finditer(regex, self.code):
            kind = match.lastgroup
            value = match.group(kind)
            column = match.start() - line_start + 1

            if kind == "WHITESPACE" or kind == "NEWLINE":
                if kind == "NEWLINE":
                    line_num += 1
                    line_start = match.end()
                self.tokens.append(Token(kind, value, line_num, column))
                continue

            print(f"DEBUG: Jeton détecté - type: {kind}, valeur: {value}, ligne: {line_num}, colonne: {column}")
            self.tokens.append(Token(kind, value, line_num, column))
        if not self.tokens:
            raise SyntaxError("Aucun jeton n'a été généré. Vérifiez les règles de syntaxe ou le code source.")
        return self.tokens

    def get_tokens(self):
        if not self.tokens:
            self.tokenize()
        return self.tokens
    

