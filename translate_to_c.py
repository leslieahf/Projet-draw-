
import re
import code_to_insert

def parse_or_variable(arg):
    """
    Si arg est un nombre littéral (ex: "100"), retourne int(arg).
    Si c'est un float littéral (ex: "3.14"), retourne float(arg).
    Sinon, c'est un nom de variable => retourne la chaîne telle quelle.
    """
    if re.match(r'^-?\d+$', arg):
        return int(arg)
    if re.match(r'^-?\d+\.\d+$', arg):
        return float(arg)
    return arg  # identifiant de variable ou autre chaîne brute

def get_printf_format_and_cast(variable, symbol_table):
    # (inchangé, c’est ton code existant)
    if (variable.startswith('"') and variable.endswith('"')) or \
       (variable.startswith("'") and variable.endswith("'")):
        return "%s", variable
    if re.match(r'^[-+]?\d+(\.\d+)?$', variable):
        return "%d" if "." not in variable else "%f", variable
    if variable in {"true", "false"}:
        return "%d", f"({variable} ? 1 : 0)"

    if variable not in symbol_table:
        raise ValueError(f"Variable '{variable}' not declared.")
    var_type = symbol_table[variable]["type"]
    if var_type == "int":
        return "%d", variable
    elif var_type == "float":
        return "%f", variable
    elif var_type == "bool":
        return "%d", f"({variable} ? 1 : 0)"
    elif var_type == "string":
        return "%s", f"&{variable}"
    else:
        raise ValueError(f"Unknown type for variable '{variable}'.")

def translate_to_c(draw_code):
    """
    Gère aussi la déclaration de fonctions via 'func nom(...) { ... }'
    """
    symbol_table = {}

    # 1) On effectue d’abord des remplacements basiques sur tout le code
    draw_code = draw_code.replace(" <- ", " = ")\
                         .replace(" eq ", " == ")\
                         .replace(" neq ", " != ")\
                         .replace("and", "&&")\
                         .replace(" or ", " || ")\
                         .replace("true", "1")\
                         .replace("false", "0")
    # Remplacement plus spécifique (à adapter selon tes besoins)
    draw_code = draw_code.replace("<", "infs")\
                         .replace(" <= ", " inf ")\
                         .replace(">", "sups")\
                         .replace(">=", "sup")

    # On sépare en lignes
    lines = draw_code.split("\n")
    
    # Buffers de code :
    global_functions = []
    functions_code = []  # Ici on va stocker la traduction des fonctions
    main_code = []       # Ici on va stocker la traduction de ce qui va dans main()
    window_created = [False]
    # Variable pour savoir si on est “en train” de capturer le contenu d’une fonction
    in_func = False
    current_func_name = None
    current_func_buffer = []  # Pour accumuler le corps d’une fonction

    # Petite fonction utilitaire pour la traduction d'un print
    def translate_print(match,symbol_table):
        expr = match.group(1).strip()
    
    # Détection simple
        if re.search(r'[+\-*/]', expr):
        # C'est une petite expression : print(a+b)
        # On suppose tout en int pour l'exemple
            return f'printf("%d\\n", {expr});'
        else:
        # Single token : variable ou littéral
            format_specifier, casted_variable = get_printf_format_and_cast(expr, symbol_table)
            return f'printf("{format_specifier}\\n", {casted_variable});'

    for line in lines:
        original_line = line.strip()
        
        # Détection du début d’une fonction : ex "func maFonction( x, y ) {"
        match_func_start = re.match(r'^func\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{', original_line)
        if match_func_start:
            # On entre dans une fonction
            in_func = True
            current_func_name = match_func_start.group(1)
            func_args = match_func_start.group(2).strip()
            
            return_type = "void"
            if "return 0" in draw_code:  # Simple détection, à améliorer si besoin
                return_type = "int"

            if func_args == "":
                functions_code.append(f"{return_type} {current_func_name}() {{")
            else:
                arg_list = [arg.strip() for arg in func_args.split(",") if arg.strip()]
                params_c = []
                for param in arg_list:
                    try:
                        type_part, var_name = param.split()
                        params_c.append(f"{type_part} {var_name}")
                        symbol_table[var_name] = {"type": type_part}
                    except ValueError:
                        raise ValueError(f"Invalid parameter declaration: '{param}'. Expected format 'type name'.")
                c_args = ", ".join(params_c)
                functions_code.append(f"{return_type} {current_func_name}({c_args}) {{")

            current_func_buffer = []
            continue

        # Détection de la fin d’une fonction : une ligne contenant seulement "}"
        if in_func and original_line == "}":
            # On ferme la fonction
            in_func = False
            # On ajoute toutes les lignes traduites qu’on a accumulées
            for func_line in current_func_buffer:
                # Vérifiez si la ligne contient un return sans point-virgule
                if func_line.strip().startswith("return") and not func_line.strip().endswith(";"):
                    func_line += ";"  # Ajoutez le point-virgule manquant
                functions_code.append("    " + func_line)
            # Fermeture de la fonction
            functions_code.append("}\n")
            current_func_buffer = []
            current_func_name = None
            continue

        # Si on est à l’intérieur d’une fonction, on accumule les lignes
        if in_func:
            # Ici, on peut réutiliser la logique existante de traduction,
            # mais on l’applique à current_func_buffer au lieu de main_code.
            
            translated_line = line_translator(line, functions_code, translate_print,window_created,symbol_table,global_functions)
            # On stocke le résultat
            current_func_buffer.extend(translated_line)
        
        else:
            # On est en dehors d’une fonction : on applique la même logique de traduction
            translated_line = line_translator(line, functions_code, translate_print,window_created,symbol_table,global_functions)
            main_code.extend(translated_line)

    # Maintenant qu’on a séparé le code des fonctions et le code de main(),
    # on assemble le code final
    c_code = []
    # Inclusions standard
    c_code.append("#include <SDL2/SDL.h>")
    c_code.append("#include <stdio.h>")
    c_code.append("#include <stdbool.h>")
    c_code.append("#include <SDL2/SDL_ttf.h>")
    c_code.append("#include <math.h>\n")

    c_code.extend(global_functions)
    # Ajout des fonctions avant le main
    c_code.extend(functions_code)

    # Début du main
    c_code.append("int main() {\n")
    # On met le code du main avec indentation
    for line in main_code:
        c_code.append("    " + line)
    # On termine
    if code_to_insert.check_comment_in_code(c_code, "//Create window") == 1:
        code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
    c_code.append("    return 0;")
    c_code.append("}\n")

    # On joint tout
    return "\n".join(c_code)


def line_translator(line,functions_code,translate_print,window_created,symbol_table,global_functions):
    """
    Traduit **une** ligne de draw++ en une ou plusieurs lignes de C.
    Retourne une liste de lignes (sans le \n final).
    
    On factorise ici pour pouvoir réutiliser la logique
    aussi bien dans le main que dans le corps des fonctions.
    """
    line = line.strip()
    result_lines = []

    # Exemple : si la ligne commence par "freedraw", etc. on gère
    # Ici, je prends des extraits de ton code existant et je simplifie.
    if line.startswith("freedraw"):
        result_lines.append("// Freedraw: insertion du code_instructions_freedraw")
        result_lines.extend(code_to_insert.code_instructions_freedraw)
        result_lines.extend(code_to_insert.code_mainProgram_freedraw)
    elif line.startswith("draw"):
        # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1: line.rfind(")")]
            # Diviser les arguments
            raw_args = code_to_insert.split_arguments(arguments)
            # Traiter chaque argument
            shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)
            # Deuxième argument : couleur RGB (chaîne sous forme "255, 255, 255")
            couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
            couleur = tuple(map(int, map(str.strip, couleur_raw.split(","))))  # Convertir en tuple d'entiers
            r, g, b = couleur   # Extraire les couleurs RGB
        
            if not window_created[0]:
                result_lines.append("// Création de la fenêtre")
                result_lines.extend(code_to_insert.code_create_window)
                window_created[0] = True  
            if "carre" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                if not code_to_insert.check_comment_in_code(global_functions, "void drawCarre"):
                    global_functions.append("// Définition de la fonction drawCarre")
                    global_functions.extend(code_to_insert.code_drawCarre)
                parametres_carre = code_to_insert.get_parametres_carre(x, y, taille, r, g, b)
                result_lines.append("// Paramètres pour le carré :")
                result_lines.extend(parametres_carre)
            elif "rectangle" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                if not code_to_insert.check_comment_in_code(global_functions, "void drawRectangle"):
                    global_functions.append("// Définition de la fonction drawRectangle")
                    global_functions.extend(code_to_insert.code_drawRectangle)
                parametres_rectangle = code_to_insert.get_parametres_rectangle(x, y, taille, r, g, b)
                result_lines.append("// Paramètres pour le rectangle :")
                result_lines.extend(parametres_rectangle)
            elif "cercle" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(coord.strip() for coord in coordonnees_raw.split(","))  # Conserver les valeurs telles quelles
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées (elles restent des chaînes pour permettre des variables comme "i")
                if not code_to_insert.check_comment_in_code(global_functions, "void drawCercle"):
                    global_functions.append("// Définition de la fonction drawCercle")
                    global_functions.extend(code_to_insert.code_drawCercle)
                parametres_cercle = code_to_insert.get_parametres_cercle(x, y, taille, r, g, b)
                result_lines.append("// Paramètres pour le cercle :")
                result_lines.extend(parametres_cercle)
            elif "triangle" in line:
                # Extraire les coordonnées
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets
                coordonnees = list(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en liste d'entiers
                if len(coordonnees) != 6:
                    raise ValueError("Un triangle nécessite exactement 6 coordonnées (x1, y1, x2, y2, x3, y3).")
                x1, y1, x2, y2, x3, y3 = coordonnees  # Extraire les 6 valeurs
                r, g, b = couleur  # Couleur RGB
                # Ajouter la fonction drawTriangle si elle n'existe pas
                if not code_to_insert.check_comment_in_code(global_functions, "void drawTriangle"):
                    global_functions.append("// Définition de la fonction drawTriangle")
                    global_functions.extend(code_to_insert.code_drawTriangle)
                parametres_triangle = code_to_insert.get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b)
                result_lines.append("// Paramètres pour le triangle:")
                result_lines.extend(parametres_triangle)
            elif "polygon" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                types_polygon = int(raw_args[4])
                if not code_to_insert.check_comment_in_code(global_functions, "void drawPolygon"):
                    global_functions.append("// Définition de la fonction drawPolygon")
                    global_functions.extend(code_to_insert.code_drawPolygon)
                parametres_polygon = code_to_insert.get_parametres_polygone(x, y, taille,types_polygon, r, g, b)
                result_lines.append("// Paramètres pour le polygone:")
                result_lines.extend(parametres_polygon)
            elif "losange" in line:
                 # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                x, y = coordonnees  # Extraire les coordonnées
                largeur=int(raw_args[3])
                hauteur=int(raw_args[4])
                if not code_to_insert.check_comment_in_code(global_functions, "void drawLosange"):
                    global_functions.append("// Définition de la fonction drawLosange")
                    global_functions.extend(code_to_insert.code_drawLosange)
                parametres_losange = code_to_insert.get_parametres_losange(x, y, largeur,hauteur, r, g, b)
                result_lines.append("// Paramètres pour le losange:")
                result_lines.extend(parametres_losange)
            elif "trapeze" in line:
               # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                x, y = coordonnees  # Extraire les coordonnées
                # Extraction des arguments
                largeur_haut = int(raw_args[3])
                largeur_bas = int(raw_args[4])
                hauteur = int(raw_args[5])
                r, g, b = couleur  # Couleur RGB
                # Insérer le code pour dessiner le trapèze
                if not code_to_insert.check_comment_in_code(global_functions, "void drawTrapeze"):
                    global_functions.append("// Définition de la fonction drawTrapeze")
                    global_functions.extend(code_to_insert.code_drawTrapeze)
                parametres_trapeze = code_to_insert.get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b)
                result_lines.append("// Paramètres pour le trapeze:")
                result_lines.extend(parametres_trapeze)
            elif "line" in line:
                # Extraire les arguments : coordonnées x1, y1, x2, y2, et couleur RGB
                coordonnees_raw = raw_args[2].strip("\"")  # Coordonnées sous forme de "x1, y1, x2, y2"
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple (x1, y1, x2, y2)
                r, g, b = couleur  # Couleur RGB
                x1, y1, x2, y2 = coordonnees  # Extraire les coordonnées x1, y1, x2, y2
                # Ajouter la fonction drawLine si elle n'existe pas déjà
                if not code_to_insert.check_comment_in_code(global_functions, "void drawLine"):
                    global_functions.append("// Définition de la fonction drawLine")
                    global_functions.extend(code_to_insert.code_drawLine)
                # Générer les paramètres pour dessiner la ligne
                parametres_line = code_to_insert.get_parametres_line(x1, y1, x2, y2, r, g, b)
                result_lines.append("// Paramètres pour le line:")
                result_lines.extend(parametres_line)
    elif line.startswith("window"):
        # gère la fenêtre
        result_lines.append("// window(...) - idem")
    elif line.startswith("call "):
        # Appel de fonction
        match_call = re.match(r'^call\s+([a-zA-Z_]\w*)\s*\((.*)\)$', line)
        if match_call:
            function_name = match_call.group(1)
            args = match_call.group(2).strip()
            if args == "":
                result_lines.append(f"{function_name}();")
            else:
                result_lines.append(f"{function_name}({args});")
        else:
            # version sans parenthèses ?
            match_call_no_paren = re.match(r'^call\s+([a-zA-Z_]\w*)$', line)
            if match_call_no_paren:
                function_name = match_call_no_paren.group(1)
                result_lines.append(f"{function_name}();")
            else:
                raise ValueError(f"Syntax error in function call: '{line}'")
    
    elif "=" in line and not re.search(r'\b(for|if|while)\b', line):
        left_side, right_side = line.split("=", 1)
        var_name = left_side.strip()
        value = right_side.strip()

        # Vérifier si la valeur est une expression
        if re.search(r'[+\-*/]', value):
            terms = re.split(r'([+\-*/])', value)
            for term in terms:
                term = term.strip()
                if re.match(r'[a-zA-Z_]\w*', term) and term not in {'+', '-', '*', '/'}:
                    if term not in symbol_table:
                        raise ValueError(f"Variable '{term}' not declared.")
                    # Vérifiez le type de la variable utilisée
                    if symbol_table[term]["type"] != "int":
                        raise ValueError(f"Invalid type '{symbol_table[term]['type']}' for variable '{term}' in expression.")
            result_lines.append(f"int {var_name} = {value};")
            var_type = "int"
        elif re.match(r'^-?\d+\.\d+$', value):
            var_type = "float"
            result_lines.append(f"float {var_name} = {value};")
        elif re.match(r'^-?\d+$', value):
            var_type = "int"
            result_lines.append(f"int {var_name} = {value};")
        elif re.match(r'^".*"$', value):
            var_type = "string"
            result_lines.append(f"char* {var_name} = {value};")
        else:
            # On suppose que la valeur est une autre variable
            if value not in symbol_table:
                raise ValueError(f"Variable '{value}' not declared.")
            var_type = symbol_table[value]["type"]
            result_lines.append(f"{var_type} {var_name} = {value};")

        # Mettre à jour la symbol_table avec la nouvelle variable
        symbol_table[var_name] = {"type": var_type}


    elif line.startswith("print"):
        line = re.sub(r'print\((.+?)\)',
                      lambda m: translate_print(m, symbol_table),
                      line)
        result_lines.append(line + ";")

    else:
        # Par défaut, on laisse la ligne telle quelle
        result_lines.append(line)

    return result_lines
