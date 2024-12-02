import re

def translate_to_c(draw_code):
    # Remplacer la syntaxe Draw++ par la syntaxe C
    draw_code = draw_code.replace(" <- ", " = ")  # Affectation en Draw++ vers C
    draw_code = draw_code.replace(" eq ", " == ")  # Vérification d'égalité
    draw_code = draw_code.replace(" neq ", " != ")  # Vérification d'inégalité
    draw_code = draw_code.replace("&", "&&")  # AND en Draw++ vers C
    draw_code = draw_code.replace(" OR ", " || ")  # OR en Draw++ vers C
    draw_code = draw_code.replace("function", "void")  # Fonction en Draw++ vers C
    draw_code = draw_code.replace(" if() {}", "if")  # Condition en Draw++ vers C
    draw_code = draw_code.replace(" else", "else")  # Else en Draw++ vers C

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
       
        elif line.startswith("draw"): 
            # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1: line.rfind(")")]

            # Diviser les arguments intelligemment en tenant compte des guillemets
            def split_arguments(argument_string):
                """Divise une chaîne d'arguments en morceaux tout en respectant les guillemets et les virgules."""
                args = []
                current = ""
                in_quotes = False  # Flag pour savoir si on est à l'intérieur de guillemets
                for char in argument_string:
                    if char == "\"":  # Toggle l'état des guillemets
                        in_quotes = not in_quotes
                    elif char == "," and not in_quotes:
                        # Si on rencontre une virgule hors des guillemets, on termine un argument
                        args.append(current.strip())
                        current = ""
                    else:
                        current += char
                # Ajouter le dernier argument
                if current:
                    args.append(current.strip())
                return args

            # Diviser les arguments
            raw_args = split_arguments(arguments)

            # Traiter chaque argument
            shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)

            # Deuxième argument : couleur RGB (chaîne sous forme "255, 255, 255")
            couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
            couleur = tuple(map(int, map(str.strip, couleur_raw.split(","))))  # Convertir en tuple d'entiers

            # Troisième argument : coordonnées (x, y) sous forme "10,10"
            coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
            coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers

            # Quatrième argument : taille
            taille = int(raw_args[3])

            # Assigner les sous-valeurs
            x, y = coordonnees  # Extraire les coordonnées
            r, g, b = couleur   # Extraire les couleurs RGB

            from code_to_insert import code_create_window, check_comment_in_code, insert_after_line
            if check_comment_in_code(c_code, "//Create window") == 0:
                insert_after_line(c_code, "int main() {", code_create_window)

            if shape == "carre" in line:
                from code_to_insert import insert_after_line, code_drawCarre,check_comment_in_code
                if check_comment_in_code(c_code, "void drawCarre") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawCarre)
                from code_to_insert import get_parametres_carre, insert_code_after_last_occurrence
                parametres_carre = get_parametres_carre(x, y, taille, r, g, b)
                if check_comment_in_code(c_code, "//Parametres carre") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_carre)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres carre", parametres_carre)
                    
            elif shape == "rectangle" in line: 
                from code_to_insert import insert_after_line, code_drawRectangle,check_comment_in_code
                if check_comment_in_code(c_code, "void drawRectangle") == 0:
                    insert_after_line(c_code, "#include <stdbool.h>", code_drawRectangle)
                from code_to_insert import get_parametres_rectangle, insert_code_after_last_occurrence
                parametres_rectangle = get_parametres_rectangle(x, y, taille, r, g, b)
                if check_comment_in_code(c_code, "//Parametres rectangle") == 0:
                    insert_after_line(c_code, "SDL_RenderClear(renderer);", parametres_rectangle)   
                else :
                    insert_code_after_last_occurrence(c_code, "//Fin parametres rectangle", parametres_rectangle)
                    
                
            elif shape == "cercle" in line:
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


        elif line.startswith("window"):
            pattern = r"window\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)"
            # Effectuer la correspondance avec la chaîne
            match = re.match(pattern, line)
            x = int(match.group(1))
            y = int(match.group(2))
            c_code.append(f"int x_window = {x};        // dimension fenetre x")
            c_code.append(f"int y_window = {y};        // dimension fenetre y")
            c_code.append("SDL_Init(SDL_INIT_VIDEO);  // Initialiser SDL")
            c_code.append('SDL_Window* window = SDL_CreateWindow("Dessin", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, x_window, y_window, SDL_WINDOW_SHOWN);')
            c_code.append("SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);")
            c_code.append("bool running = true;  // Indique si la boucle continue")
            c_code.append("SDL_Event event;      // Événement pour capturer les actions utilisateur")
            c_code.append("")
            c_code.append("while (running) {")
            c_code.append("    while (SDL_PollEvent(&event)) {")
            c_code.append("        if (event.type == SDL_QUIT) {  // Fermer la fenêtre")
            c_code.append("            running = false;")
            c_code.append("        } else if (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE) {  // Touche \"ESC\"")
            c_code.append("            running = false;")
            c_code.append("        }")
            c_code.append("    }")
            c_code.append("}")



        elif "=" in line:
            # Essayer de déduire le type de la variable
            if re.search(r'\d+\.\d+', line):  # Si on trouve un nombre flottant
                c_code.append(f"    float {line};")
            elif re.search(r'\d', line):  # Si on trouve un chiffre entier, on le traite comme un int
                c_code.append(f"    int {line};")
            elif re.search(r'"', line):  # Si on trouve des guillemets, on le traite comme une chaîne
                c_code.append(f"    char* {line};")
            else:  # Sinon, on traite comme un type générique, ici "int" par défaut
                c_code.append(f"    int {line};")
        elif re.search(r'\bprint\b', line):
            c_code.append(f"    {re.sub(r'\bprint\b', 'printf', line)};")
        else:
            c_code.append(f"    {line}")  # Laisser la ligne telle quelle, avec indentation
        
    c_code.append("    return 0;")
    c_code.append("}")  # Fin de la fonction main

    # Retourner le code complet C avec le main inclus
    return "\n".join(c_code)
