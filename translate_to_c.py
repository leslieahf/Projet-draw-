import re

def get_printf_format_and_cast(variable, symbol_table):
    # Si le variable est un littéral string
    if (variable.startswith('"') and variable.endswith('"')) or (variable.startswith("'") and variable.endswith("'")):
        return "%s", variable  # Retourne directement le littéral

    # Si la variable est une constante numérique
    if re.match(r'^[-+]?\d+(\.\d+)?$', variable):
        return "%d" if "." not in variable else "%f", variable

    # Si la variable est une booléenne
    if variable in {"true", "false"}:
        return "%d", f"({variable} ? 1 : 0)"  # true -> 1, false -> 0

    # Vérifier si la variable est déclarée dans le symbol_table
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
        return "%s", f"&{variable}"  # Ajout de & pour les strings
    else:
        raise ValueError(f"Unknown type for variable '{variable}'.")

def translate_to_c(draw_code):
    symbol_table = {}
    draw_code = draw_code.replace(" <- ", " = ").replace(" eq ", " == ").replace(" neq ", " != ")
    draw_code = draw_code.replace("and", "&&").replace(" or ", " || ").replace("true", "1").replace("false", "0")
    draw_code = draw_code.replace("<", "infs").replace(" <= ", " inf ").replace(">", "sups").replace(">=", "sup")
    def track_variable(line):
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if match:
            variable_name = match.group(1)
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

    def translate_print(match):
        variable = match.group(1).strip()
        try:
            format_specifier, casted_variable = get_printf_format_and_cast(variable, symbol_table)
            return f'printf("{format_specifier}\\n", {casted_variable});'
        except ValueError as e:
            raise ValueError(f"Error translating print statement: {e}")
        
    # Séparer le code en lignes
    lines = draw_code.split("\n")
    
    # Construire le code C à l'intérieur de main()
    c_code = ["#include <SDL2/SDL.h>"]
    c_code.append("#include <stdio.h>")
    c_code.append("#include <stdbool.h>")
    c_code.append("")
 
    c_code.append("int main() {")  # Début de la fonction main
 
    for i, line in enumerate(lines):
        line = line.strip()  # Supprimer les espaces autour de la ligne
        # Si c'est une fonction ou une condition, on ne modifie pas le point-virgule
 
        if line.startswith("function") or line.startswith("if") or line.startswith("else"):
            c_code.append(f"    {line}")  # Ajouter avec une indentation de 4 espaces
            # Si c'est une affectation ou une déclaration, on ajoute un point-virgule pour C
       
        elif line.startswith("freedraw"):
            code_to_insert.insert_after_line(c_code,"#include <math.h>", code_to_insert.code_instructions_freedraw)
            code_to_insert.insert_after_line(c_code, "int main() {", code_to_insert.code_mainProgram_freedraw)
            
        elif line.startswith("draw"):
            # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1: line.rfind(")")]
 
            from code_to_insert import split_arguments
            
            # Diviser les arguments
            raw_args = split_arguments(arguments)
 
            # Traiter chaque argument
            shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)
 
            # Deuxième argument : couleur RGB (chaîne sous forme "255, 255, 255")
            couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
            couleur = tuple(map(int, map(str.strip, couleur_raw.split(","))))  # Convertir en tuple d'entiers
 
            r, g, b = couleur   # Extraire les couleurs RGB
 
            from code_to_insert import code_create_window, check_comment_in_code, insert_after_line
            if check_comment_in_code(c_code, "//Create window") == 0:
                insert_after_line(c_code, "int main() {", code_create_window)
 
            if "carre" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
 
                from code_to_insert import insert_after_line, code_drawCarre,check_comment_in_code
                if check_comment_in_code(c_code, "void drawCarre") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawCarre)
                from code_to_insert import get_parametres_carre, insert_code_after_last_occurrence
                parametres_carre = get_parametres_carre(x, y, taille, r, g, b)
                if check_comment_in_code(c_code, "//Parametres carre") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_carre)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres carre", parametres_carre)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")  
            
            elif "rectangle" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                from code_to_insert import insert_after_line, code_drawRectangle,check_comment_in_code
                if check_comment_in_code(c_code, "void drawRectangle") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawRectangle)
                from code_to_insert import get_parametres_rectangle, insert_code_after_last_occurrence
                parametres_rectangle = get_parametres_rectangle(x, y, taille, r, g, b)
                if check_comment_in_code(c_code, "//Parametres rectangle") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_rectangle)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres rectangle", parametres_rectangle)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")  
                
            elif "cercle" in line:
                 # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                from code_to_insert import insert_after_line, code_drawCercle,check_comment_in_code
                if check_comment_in_code(c_code, "void drawCercle") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawCercle)
                from code_to_insert import get_parametres_cercle, insert_code_after_last_occurrence
                parametres_cercle = get_parametres_cercle(x, y, taille, r, g, b)
                if check_comment_in_code(c_code, "//Parametres cercle") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_cercle)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_cercle)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            
            elif "triangle" in line:
                # Extraire les coordonnées
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets
                coordonnees = list(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en liste d'entiers
                
                if len(coordonnees) != 6:
                    raise ValueError("Un triangle nécessite exactement 6 coordonnées (x1, y1, x2, y2, x3, y3).")
 
                x1, y1, x2, y2, x3, y3 = coordonnees  # Extraire les 6 valeurs
                r, g, b = couleur  # Couleur RGB
 
                # Ajouter la fonction drawTriangle si elle n'existe pas
                from code_to_insert import insert_after_line, code_drawTriangle, check_comment_in_code
                if check_comment_in_code(c_code, "void drawTriangle") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawTriangle)
 
                # Générer les paramètres pour dessiner le triangle
                from code_to_insert import get_parametres_triangle, insert_code_after_last_occurrence
                parametres_triangle = get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b)
 
                # Insérer les paramètres dans le code généré
                if check_comment_in_code(c_code, "//Parametres triangle") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_triangle)
                else:
                    insert_code_after_last_occurrence(c_code, "//Fin parametres triangle", parametres_triangle)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
 
            elif "polygon" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                types_polygon = int(raw_args[4])
                from code_to_insert import insert_after_line, code_drawPolygon,check_comment_in_code
                if check_comment_in_code(c_code, "void drawPolygon") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawPolygon)
                from code_to_insert import get_parametres_polygone, insert_code_after_last_occurrence
                parametres_polygon = get_parametres_polygone(x, y, taille,types_polygon, r, g, b)
                if check_comment_in_code(c_code, "//Parametres polygon") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_polygon)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_polygon)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            
            elif "losange" in line:
                 # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                x, y = coordonnees  # Extraire les coordonnées
                largeur=int(raw_args[3])
                hauteur=int(raw_args[4])
                from code_to_insert import insert_after_line, code_drawLosange,check_comment_in_code
                if check_comment_in_code(c_code, "void drawLosange") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawLosange)
                from code_to_insert import get_parametres_losange, insert_code_after_last_occurrence
                parametres_losange = get_parametres_losange(x, y, largeur,hauteur, r, g, b)
                if check_comment_in_code(c_code, "//Parametres losange") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_losange)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_losange)
                
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
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
                from code_to_insert import insert_after_line, code_drawTrapeze, check_comment_in_code
                if check_comment_in_code(c_code, "void drawTrapeze") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawTrapeze)
 
                from code_to_insert import get_parametres_trapeze, insert_code_after_last_occurrence
                parametres_trapeze = get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b)
 
                # Ajouter les paramètres dans le code
                if check_comment_in_code(c_code, "//Parametres trapeze") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_trapeze)
                else:
                    insert_code_after_last_occurrence(c_code, "//Fin parametres trapeze", parametres_trapeze)
 
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            
            elif "line" in line:
                # Extraire les arguments : coordonnées x1, y1, x2, y2, et couleur RGB
                coordonnees_raw = raw_args[2].strip("\"")  # Coordonnées sous forme de "x1, y1, x2, y2"
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple (x1, y1, x2, y2)
                r, g, b = couleur  # Couleur RGB
 
                x1, y1, x2, y2 = coordonnees  # Extraire les coordonnées x1, y1, x2, y2
 
                # Ajouter la fonction drawLine si elle n'existe pas déjà
                from code_to_insert import insert_after_line, code_drawLine, check_comment_in_code
                if check_comment_in_code(c_code, "void drawLine") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawLine)
 
                # Générer les paramètres pour dessiner la ligne
                from code_to_insert import get_parametres_line, insert_code_after_last_occurrence
                parametres_line = get_parametres_line(x1, y1, x2, y2, r, g, b)
 
            # Insérer les paramètres dans le code généré
                if check_comment_in_code(c_code, "//Parametres line") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_line)
                else:
                    insert_code_after_last_occurrence(c_code, "//Fin parametres line", parametres_line)
                from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
        
        elif line.startswith("window"):
            # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1: line.rfind(")")]
            from code_to_insert import extract_window_params
            coordonnees, x, y, r, g, b = extract_window_params(arguments)
            from code_to_insert import get_parametres_window, check_comment_in_code
            from code_to_insert import code_create_window_modify, code_staywindow_open, get_parametres_window, insert_code_if_comment_not_present, check_comment_in_code, insert_code_before_first_occurrence, insert_after_line
            parametres_window = get_parametres_window(x, y, r, g, b)
            if check_comment_in_code(c_code, "//Create window") == 0:
                if check_comment_in_code(c_code, "{ //debut" ) == 1: 
                    insert_code_before_first_occurrence(c_code, "{ //debut", code_create_window_modify)
                else :
                    c_code.extend(code_create_window_modify)
                insert_code_before_first_occurrence(c_code, "//Create window", parametres_window)
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            else :
                from code_to_insert import remove_lines_after_keyword, code_create_window_modify, code_staywindow_open, insert_code_before_first_occurrence, insert_after_line, insert_code_if_comment_not_present
                if check_comment_in_code(c_code, "   //Parametres window") == 1:
                    remove_lines_after_keyword(c_code, "   //Parametres window", 14)
                else : 
                    remove_lines_after_keyword(c_code, "//Create window", 6)
                if check_comment_in_code(c_code, "{ //debut" ) == 1: 
                        insert_code_before_first_occurrence(c_code, "{ //debut", code_create_window_modify)
                else :
                    c_code.extend(code_create_window_modify)
                insert_code_before_first_occurrence(c_code, "//Create window", parametres_window)
                insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
        
        
        if "=" in line:
            track_variable(line)
            var_name = line.split(" = ")[0].strip()
            var_type = symbol_table[var_name]["type"]
            if var_type == "int":
                c_code.append(f"    int {line};")
            elif var_type == "float":
                c_code.append(f"    float {line};")
            elif var_type == "bool":
                c_code.append(f"    int {line};")
            elif var_type == "string":
                c_code.append(f"    char* {line};")
            else:
                c_code.append(f"    {line};")
        elif line.startswith("print"):
            line = re.sub(r'print\((.+?)\)', translate_print, line)
            c_code.append(f"    {line}")
        else:
            c_code.append(f"    {line};")

    c_code.append("    return 0;")
    c_code.append("}")  # Fin de la fonction main
 
    # Retourner le code complet C avec le main inclus
    return "\n".join(c_code)


