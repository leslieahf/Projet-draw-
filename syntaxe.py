from tok import Lexer
from parseur import Parser


def validate_code(draw_code):
    errors = []
    tokens = []
    ast = []

    try:
        # STEP 1: Tokenisation
        lexer = Lexer(draw_code)
        tokens = lexer.get_tokens()
        

        # STEP 2  : Parsing
        parser = Parser(tokens)
        ast = parser.parse()


    except Exception as e:
        # Captur all the errors
        errors.append(f"Erreur lors de la validation : {str(e)}")
        print(f"DEBUG: Exception capturée - {str(e)}")

    return errors, tokens, ast
