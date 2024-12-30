from tok import Lexer
from parseur import Parser


def validate_code(draw_code):
    errors = []
    tokens = []
    ast = []

    try:
        # Étape 1 : Tokenisation
        lexer = Lexer(draw_code)
        tokens = lexer.get_tokens()
        print("DEBUG: Jetons générés :", tokens)

        # Étape 2 : Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        print("DEBUG: AST généré :", ast)

    except Exception as e:
        # Capture toutes les erreurs
        errors.append(f"Erreur lors de la validation : {str(e)}")
        print(f"DEBUG: Exception capturée - {str(e)}")

    return errors, tokens, ast
