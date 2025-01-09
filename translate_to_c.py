import re

# =======================
# 1) Gestion "print(a+b)"
# =======================
def parse_arg(arg_str):
    """
    Si arg_str représente un entier (ex: "100"), on le renvoie sous forme de chaîne "100".
    Si c'est un float (ex: "3.14"), on le renvoie tel quel "3.14".
    Sinon, on suppose que c'est une variable => on renvoie "f", "x", etc.
    L'idée étant de ne pas faire int(...) quand c'est une variable.
    """
    # Nettoyer l'argument
    arg_str = arg_str.strip()

    # Est-ce un entier ?
    if re.match(r'^-?\d+$', arg_str):
        return arg_str  # c'est déjà un littéral int, ex: "100"

    # Est-ce un float ?
    if re.match(r'^-?\d+\.\d+$', arg_str):
        return arg_str  # c'est un littéral float, ex: "3.14"

    # Sinon, c'est un nom de variable (ou expression)
    return arg_str 
def get_printf_format_and_cast(expr, symbol_table):
    """
    Si expr est une variable unique, on regarde son type.
    Sinon, si c'est un littéral, on le traduit direct.
    Sinon, on le traite comme une expression (a+b, etc.).
    """
    # 1) Si expr est déjà dans la table des symboles
    if expr in symbol_table:
        var_type = symbol_table[expr]["type"]
        if var_type == "int":
            return "%d", expr
        elif var_type == "float":
            return "%f", expr
        elif var_type == "bool":
            return "%d", f"({expr} ? 1 : 0)"
        elif var_type == "string":
            return "%s", f"&{expr}"
        else:
            raise ValueError(f"Unknown type for variable '{expr}'.")

    # 2) Vérifier si c'est un littéral
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return "%s", expr  # littéral string
    if re.match(r'^[-+]?\d+(\.\d+)?$', expr):  # nombre pur
        return ("%d", expr) if "." not in expr else ("%f", expr)
    if expr in {"true", "false"}:
        return "%d", f"({expr} ? 1 : 0)"

    # 3) Sinon, c'est probablement une expression
    tokens = re.findall(r'[a-zA-Z_]\w*|\d+\.\d+|\d+', expr)
    is_float = False
    for t in tokens:
        if '.' in t and re.match(r'^\d+\.\d+$', t):
            is_float = True
            break
        if t in symbol_table:
            if symbol_table[t]["type"] == "float":
                is_float = True
                break

    fmt = "%f" if is_float else "%d"
    return fmt, expr

def translate_print(match, symbol_table):
    """
    Remplace print(...) par printf(...)
    """
    expr = match.group(1).strip()
    fmt, casted_expr = get_printf_format_and_cast(expr, symbol_table)
    return f'printf("{fmt}\\n", {casted_expr});'


# ==============================
# 2) Le "vrai" traducteur global
# ==============================

def translate_to_c(draw_code):
    """
    Gère :
      - La séparation des fonctions `func nom(...) { ... }`
      - La traduction du code principal dans main()
      - L'insertion de tout le code SDL (draw, window, etc.)
      - La gestion des variables (symbol_table)
    """

    # Table des symboles (variables déclarées, type, etc.)
    symbol_table = {}

    # Remplacements basiques
    draw_code = draw_code.replace(" <- ", " = ") \
                         .replace(" eq ", " == ") \
                         .replace(" neq ", " != ") \
                         .replace("and", "&&") \
                         .replace(" or ", " || ") \
                         .replace("true", "1") \
                         .replace("false", "0") \
                         .replace("<", "infs") \
                         .replace(" <= ", " inf ") \
                         .replace(">", "sups") \
                         .replace(">=", "sup")

    # On va séparer en deux morceaux:
    #  1) c_functions : liste de lignes C pour les fonctions (en dehors de main)
    #  2) main_lines  : liste de lignes qu'on traduira dans main

    c_functions = []
    main_lines = []

    lines = draw_code.split("\n")
    i = 0
    n = len(lines)

    # Cette fonction remplit symbol_table en fonction d'une affectation
    def track_variable(line, current_func_params=None):
        """
        Détecte et ajoute des variables dans la table des symboles, sauf si ce sont des paramètres de fonction.
        """
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if match:
            variable_name = match.group(1)
            # Ne pas ajouter les paramètres de fonction au symbol_table
            if current_func_params and variable_name in current_func_params:
                return
        value = match.group(2)
        if re.match(r'^[0-9]+$', value):
            symbol_table[variable_name] = {"type": "int"}
        elif re.match(r'^[0-9]+\.[0-9]+$', value):
            symbol_table[variable_name] = {"type": "float"}
        elif re.match(r'^(1|0)$', value):
            symbol_table[variable_name] = {"type": "bool"}
        elif re.match(r'^".*"$', value):
            symbol_table[variable_name] = {"type": "string"}
        else:
            symbol_table[variable_name] = {"type": "unknown"}

    def translate_block(block_lines, current_func_params=None):
        """
        Traduit un bloc de lignes (que ce soit un corps de fonction ou le main)
        en instructions C. 

        - Gère "call nom(...)", "print(...)", "draw(...)", "window(...)", etc.
        - Gère la déclaration de variable en fonction du type détecté (int, float, etc.).
        - Si is_function_body=True, on peut adapter légèrement (mais ici, on fait pareil).
        """
        c_block = []
        for line in block_lines:
            line = line.strip()
            if not line:
                continue

            # 1) "call nomFonction(...)" => "nomFonction(...);"
            if line.startswith("call "):
                match_call = re.match(r'^call\s+([a-zA-Z_]\w*)\s*\((.*)\)$', line)
                if match_call:
                    fname = match_call.group(1)
                    args = match_call.group(2).strip()
                    if args == "":
                        c_block.append(f"{fname}();")
                    else:
                        c_block.append(f"{fname}({args});")
                else:
                    # S'il n'y a pas de parenthèses
                    match_call_no_paren = re.match(r'^call\s+([a-zA-Z_]\w*)$', line)
                    if match_call_no_paren:
                        fname = match_call_no_paren.group(1)
                        c_block.append(f"{fname}();")
                    else:
                        raise ValueError(f"Syntax error in function call: '{line}'")
                continue

            # 2) "print(...)"
            if line.startswith("print"):
                new_line = re.sub(r'print\((.+?)\)', 
                                  lambda m: translate_print(m, symbol_table),
                                  line)
                c_block.append(new_line)
                continue

            # 3) "draw(...)" => ici, on ferait l'appel à tes routines SDL (code_to_insert, etc.)
            if line.startswith("draw"):
                  # Extraire les informations entre les parenthèses
                arguments = line[line.find("(") + 1: line.rfind(")")]
    
                from code_to_insert import split_arguments
                
                # Diviser les arguments
                raw_args = split_arguments(arguments)
    
                # Traiter chaque argument
                shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)
    
                # Deuxième argument : couleur RGB (chaîne sous forme "255, 255, 255")
                couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
                couleur_parts = map(str.strip, couleur_raw.split(","))  # Diviser en parties (chaînes)

                # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                r, g, b = (parse_arg(part) for part in couleur_parts)

    
                from code_to_insert import code_create_window, check_comment_in_code, insert_after_line
                if check_comment_in_code(final_code, "//Create window") == 0:
                    insert_after_line(final_code, "int main() {", code_create_window)
    
                if "carre" in line:
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)

                    x, y = coordonnees  # Extraire les coordonnées
                    taille = parse_arg((raw_args[3]))
                    from code_to_insert import insert_after_line, code_drawCarre,check_comment_in_code
                    if check_comment_in_code(final_code, "void drawCarre") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawCarre)
                    from code_to_insert import get_parametres_carre, insert_code_after_last_occurrence
                    parametres_carre = get_parametres_carre(x, y, taille, r, g, b)
                    if check_comment_in_code(final_code, "//Parametres carre") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_carre)   
                    else :
                        insert_code_after_last_occurrence(final_code, "//Fin parametres carre", parametres_carre)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")  
                
                elif "rectangle" in line:
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)

                    x, y = coordonnees  # Extraire les coordonnées
                    taille = parse_arg((raw_args[3]))
                    from code_to_insert import insert_after_line, code_drawRectangle,check_comment_in_code
                    if check_comment_in_code(final_code, "void drawRectangle") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawRectangle)
                    from code_to_insert import get_parametres_rectangle, insert_code_after_last_occurrence
                    parametres_rectangle = get_parametres_rectangle(x, y, taille, r, g, b)
                    if check_comment_in_code(final_code, "//Parametres rectangle") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_rectangle)   
                    else :
                        insert_code_after_last_occurrence(final_code, "//Fin parametres rectangle", parametres_rectangle)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")  
                    
                elif "cercle" in line:
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)

                    x, y = coordonnees  # Extraire les coordonnées
                    taille = parse_arg((raw_args[3]))
                    from code_to_insert import insert_after_line, code_drawCercle,check_comment_in_code
                    if check_comment_in_code(final_code, "void drawCercle") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawCercle)
                    from code_to_insert import get_parametres_cercle, insert_code_after_last_occurrence
                    parametres_cercle = get_parametres_cercle(x, y, taille, r, g, b)
                    if check_comment_in_code(final_code, "//Parametres cercle") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_cercle)   
                    else :
                        insert_code_after_last_occurrence(final_code, "//Fin parametres cercle", parametres_cercle)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                
                elif "triangle" in line:
                    # Extraire les coordonnées
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)

                    if len(coordonnees) != 6:
                        raise ValueError("Un triangle nécessite exactement 6 coordonnées (x1, y1, x2, y2, x3, y3).")
    
                    x1, y1, x2, y2, x3, y3 = coordonnees  # Extraire les 6 valeurs
    
                    # Ajouter la fonction drawTriangle si elle n'existe pas
                    from code_to_insert import insert_after_line, code_drawTriangle, check_comment_in_code
                    if check_comment_in_code(final_code, "void drawTriangle") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawTriangle)
    
                    # Générer les paramètres pour dessiner le triangle
                    from code_to_insert import get_parametres_triangle, insert_code_after_last_occurrence
                    parametres_triangle = get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b)
    
                    # Insérer les paramètres dans le code généré
                    if check_comment_in_code(final_code, "//Parametres triangle") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_triangle)
                    else:
                        insert_code_after_last_occurrence(final_code, "//Fin parametres triangle", parametres_triangle)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
    
                elif "polygon" in line:
                    # Troisième argument : coordonnées (x, y) sous forme "10,10"
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)
                    x, y = coordonnees  # Extraire les coordonnées
                    taille = parse_arg((raw_args[3]))
                   
                    types_polygon = parse_arg((raw_args[4]))
                    from code_to_insert import insert_after_line, code_drawPolygon,check_comment_in_code
                    if check_comment_in_code(final_code, "void drawPolygon") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawPolygon)
                    from code_to_insert import get_parametres_polygone, insert_code_after_last_occurrence
                    parametres_polygon = get_parametres_polygone(x, y, taille,types_polygon, r, g, b)
                    if check_comment_in_code(final_code, "//Parametres polygon") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_polygon)   
                    else :
                        insert_code_after_last_occurrence(final_code, "//Fin parametres cercle", parametres_polygon)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                
                elif "losange" in line:
                    # Troisième argument : coordonnées (x, y) sous forme "10,10"
                     # Troisième argument : coordonnées (x, y) sous forme "10,10"
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)
                    x, y = coordonnees  # Extraire les coordonnées
                    largeur=parse_arg(raw_args[3])
                    hauteur=parse_arg(raw_args[4])
                    from code_to_insert import insert_after_line, code_drawLosange,check_comment_in_code
                    if check_comment_in_code(final_code, "void drawLosange") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawLosange)
                    from code_to_insert import get_parametres_losange, insert_code_after_last_occurrence
                    parametres_losange = get_parametres_losange(x, y, largeur,hauteur, r, g, b)
                    if check_comment_in_code(final_code, "//Parametres losange") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_losange)   
                    else :
                        insert_code_after_last_occurrence(final_code, "//Fin parametres cercle", parametres_losange)
                    
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                elif "trapeze" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)  # Convertir en tuple d'entiers
                    x, y = coordonnees  # Extraire les coordonnées
                    # Extraction des arguments
                    largeur_haut = parse_arg((raw_args[3]))
                    largeur_bas = parse_arg((raw_args[4]))
                    hauteur = parse_arg((raw_args[5]))
    
                    # Insérer le code pour dessiner le trapèze
                    from code_to_insert import insert_after_line, code_drawTrapeze, check_comment_in_code
                    if check_comment_in_code(final_code, "void drawTrapeze") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawTrapeze)
    
                    from code_to_insert import get_parametres_trapeze, insert_code_after_last_occurrence
                    parametres_trapeze = get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b)
    
                    # Ajouter les paramètres dans le code
                    if check_comment_in_code(final_code, "//Parametres trapeze") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_trapeze)
                    else:
                        insert_code_after_last_occurrence(final_code, "//Fin parametres trapeze", parametres_trapeze)
    
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                
                elif "line" in line:
                    # Extraire les arguments : coordonnées x1, y1, x2, y2, et couleur RGB
                    coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                    coordonnees_parts = map(str.strip, coordonnees_raw.split(","))  # Diviser en parties (chaînes)

                    # Appliquer parse_arg pour permettre des variables ou des valeurs littérales
                    coordonnees = tuple(parse_arg(part) for part in coordonnees_parts)  # Convertir en tuple d'entiers
                    x1, y1, x2, y2 = coordonnees  # Extraire les coordonnées x1, y1, x2, y2
    
                    # Ajouter la fonction drawLine si elle n'existe pas déjà
                    from code_to_insert import insert_after_line, code_drawLine, check_comment_in_code
                    if check_comment_in_code(final_code, "void drawLine") == 0:
                        insert_after_line(final_code, "#include <stdbool.h>", code_drawLine)
    
                    # Générer les paramètres pour dessiner la ligne
                    from code_to_insert import get_parametres_line, insert_code_after_last_occurrence
                    parametres_line = get_parametres_line(x1, y1, x2, y2, r, g, b)
    
                # Insérer les paramètres dans le code généré
                    if check_comment_in_code(final_code, "//Parametres line") == 0:
                        insert_after_line(final_code, "SDL_RenderClear(renderer);", parametres_line)
                    else:
                        insert_code_after_last_occurrence(final_code, "//Fin parametres line", parametres_line)
                    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                    insert_code_if_comment_not_present(final_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            
                    # -- Insère ton code existant pour gérer draw(...) --
                    #   ex: shape = raw_args[0], couleur = raw_args[1]...
                    #   (par souci de concision, on mettra un commentaire)
                    c_block.append(f"// [SDL] traduction de: {line}")
                    continue

            # 4) "window(...)" => pareil, on insère le code SDL correspondant
            if line.startswith("window"):
                c_block.append(f"// [SDL] traduction de: {line}")
                continue

            # 5) "if", "else", etc.
            if line.startswith("if") or line.startswith("else"):
                c_block.append(line)
                continue

            # 6) Les affectations (x = 10, etc.)
            if "=" in line and not re.search(r'\b(for|if|while)\b', line):
                track_variable(line, current_func_params)
                var_name = line.split(" = ")[0].strip()
                if current_func_params and var_name in current_func_params:
                    c_block.append(f"{line};")  # Pas de redéclaration pour les paramètres
                else:
                    var_type = symbol_table.get(var_name, {}).get("type", "unknown")
                    if var_type == "int":
                        c_block.append(f"int {line};")
                    elif var_type == "float":
                        c_block.append(f"float {line};")
                    elif var_type == "bool":
                        c_block.append(f"int {line};")
                    elif var_type == "string":
                        c_block.append(f"char* {line};")
                continue

            # 7) Autre chose => on l'insère tel quel
            c_block.append(f"{line};")

        return c_block

    # ================
    # 3) Parsing global
    # ================

    while i < n:
        line = lines[i].strip()

        # Détection d'une fonction
        if line.startswith("func "):
            match_func = re.match(r'^func\s+([a-zA-Z_]\w*)\s*\((.*)\)\s*\{?$', line)
            if not match_func:
                raise ValueError(f"Syntax error in function definition: {line}")
            
            func_name = match_func.group(1)
            func_args = match_func.group(2).strip().split(",") if match_func.group(2).strip() else []
            func_args = [arg.strip() for arg in func_args]

            func_body = []
            brace_open = line.endswith("{")
            i += 1
            if not brace_open and i < n and lines[i].strip() == "{":
                i += 1

            while i < n:
                check_line = lines[i].strip()
                if check_line == "}":
                    i += 1
                    break
                func_body.append(check_line)
                i += 1

            # Traduction du corps de la fonction
            translated_func = translate_block(func_body, current_func_params=func_args)
            c_functions.append(f"void {func_name}({', '.join(f'int {arg}' for arg in func_args)}) {{")
            for code_line in translated_func:
                c_functions.append(f"    {code_line}")
            c_functions.append("}")
        else:
            main_lines.append(line)
            i += 1
    # ====================================
    # 4) Traduire le code de main() en C
    # ====================================

    main_translated = translate_block(main_lines)

    # =========================
    # 5) Assemblage final en C
    # =========================

    final_code = []
    # Les includes
    final_code.append('#include <SDL2/SDL.h>')
    final_code.append('#include <stdio.h>')
    final_code.append('#include <stdbool.h>')
    final_code.append('')

    # Les fonctions
    for fc_line in c_functions:
        final_code.append(fc_line)

    final_code.append('')
    final_code.append('int main() {')
    for line in main_translated:
        final_code.append(f"    {line}")
    final_code.append('    return 0;')
    final_code.append('}')

    # On renvoie le code complet
    return "\n".join(final_code)

