
#######################################################################################################################"
import re
import code_to_insert
 
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
            # Diviser les arguments
            raw_args = code_to_insert.split_arguments(arguments)
            # Traiter chaque argument
            shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)
            # Deuxième argument : couleur RGB (chaîne sous forme "255, 255, 255")
            couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
            couleur = tuple(map(int, map(str.strip, couleur_raw.split(","))))  # Convertir en tuple d'entiers
            r, g, b = couleur   # Extraire les couleurs RGB
            if code_to_insert.check_comment_in_code(c_code, "//Create window") == 0:
                code_to_insert.insert_after_line(c_code, "int main() {", code_to_insert.code_create_window)
            if "carre" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                if code_to_insert.check_comment_in_code(c_code, "void drawCarre") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawCarre)
                parametres_carre = code_to_insert.get_parametres_carre(x, y, taille, r, g, b)
                if code_to_insert.check_comment_in_code(c_code, "//Parametres carre") == 0:
                   code_to_insert.insert_after_previous_line(c_code, parametres_carre)   
                else :
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres carre", parametres_carre)
            elif "rectangle" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                if code_to_insert.check_comment_in_code(c_code, "void drawRectangle") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawRectangle)
                parametres_rectangle = code_to_insert.get_parametres_rectangle(x, y, taille, r, g, b)
                if code_to_insert.check_comment_in_code(c_code, "//Parametres rectangle") == 0:
                    code_to_insert.insert_after_previous_line(c_code, parametres_rectangle)   
                else :
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres rectangle", parametres_rectangle)
            elif "cercle" in line:
                 # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                if code_to_insert.check_comment_in_code(c_code, "void drawCercle") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawCercle)
                parametres_cercle = code_to_insert.get_parametres_cercle(x, y, taille, r, g, b)
                if code_to_insert.check_comment_in_code(c_code, "//Parametres cercle") == 0:
                    code_to_insert.insert_after_previous_line(c_code, parametres_cercle)  
                else :
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_cercle)
            elif "triangle" in line:
                # Extraire les coordonnées
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets
                coordonnees = list(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en liste d'entiers
                if len(coordonnees) != 6:
                    raise ValueError("Un triangle nécessite exactement 6 coordonnées (x1, y1, x2, y2, x3, y3).")
                x1, y1, x2, y2, x3, y3 = coordonnees  # Extraire les 6 valeurs
                r, g, b = couleur  # Couleur RGB
                # Ajouter la fonction drawTriangle si elle n'existe pas
                if code_to_insert.check_comment_in_code(c_code, "void drawTriangle") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawTriangle)
                # Générer les paramètres pour dessiner le triangle
                parametres_triangle = code_to_insert.get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b)
                # Insérer les paramètres dans le code généré
                if code_to_insert.check_comment_in_code(c_code, "//Parametres triangle") == 0:
                   code_to_insert.insert_after_previous_line(c_code, parametres_triangle)  
                else:
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres triangle", parametres_triangle)
            elif "polygon" in line:
                # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                taille = int(raw_args[3])
                x, y = coordonnees  # Extraire les coordonnées
                types_polygon = int(raw_args[4])
                if code_to_insert.check_comment_in_code(c_code, "void drawPolygon") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawPolygon)
                parametres_polygon = code_to_insert.get_parametres_polygone(x, y, taille,types_polygon, r, g, b)
                if code_to_insert.check_comment_in_code(c_code, "//Parametres polygon") == 0:
                   code_to_insert.insert_after_previous_line(c_code, parametres_polygon)    
                else :
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_polygon)
            elif "losange" in line:
                 # Troisième argument : coordonnées (x, y) sous forme "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
                x, y = coordonnees  # Extraire les coordonnées
                largeur=int(raw_args[3])
                hauteur=int(raw_args[4])
                if code_to_insert.check_comment_in_code(c_code, "void drawLosange") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawLosange)
                parametres_losange = code_to_insert.get_parametres_losange(x, y, largeur,hauteur, r, g, b)
                if  code_to_insert.check_comment_in_code(c_code, "//Parametres losange") == 0:
                    code_to_insert.insert_after_previous_line(c_code, parametres_losange)  
                else :
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres cercle", parametres_losange)
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
                if code_to_insert.check_comment_in_code(c_code, "void drawTrapeze") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawTrapeze)
                parametres_trapeze = code_to_insert.get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b)
                # Ajouter les paramètres dans le code
                if  code_to_insert. check_comment_in_code(c_code, "//Parametres trapeze") == 0:
                    code_to_insert.insert_after_previous_line(c_code, parametres_trapeze)  
                else:
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres trapeze", parametres_trapeze)
            elif "line" in line:
                # Extraire les arguments : coordonnées x1, y1, x2, y2, et couleur RGB
                coordonnees_raw = raw_args[2].strip("\"")  # Coordonnées sous forme de "x1, y1, x2, y2"
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple (x1, y1, x2, y2)
                r, g, b = couleur  # Couleur RGB
                x1, y1, x2, y2 = coordonnees  # Extraire les coordonnées x1, y1, x2, y2
                # Ajouter la fonction drawLine si elle n'existe pas déjà
                if code_to_insert.check_comment_in_code(c_code, "void drawLine") == 0:
                    code_to_insert.insert_after_line(c_code, "#include <stdbool.h>", code_to_insert.code_drawLine)
                # Générer les paramètres pour dessiner la ligne
                parametres_line = code_to_insert.get_parametres_line(x1, y1, x2, y2, r, g, b)
                # Insérer les paramètres dans le code généré
                if code_to_insert.check_comment_in_code(c_code, "//Parametres line") == 0:
                    code_to_insert.insert_after_previous_line(c_code, parametres_line)  
                else:
                    code_to_insert.insert_code_after_last_occurrence(c_code, "//Fin parametres line", parametres_line)
        elif line.startswith("window"):
            # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1: line.rfind(")")]
            coordonnees, x, y, r, g, b = code_to_insert.extract_window_params(arguments)
            if coordonnees == "full" :
                parametres_window = code_to_insert.get_parametres_window(x, y, r, g, b)
                if  code_to_insert.check_comment_in_code(c_code, "//Create window") == 0:
                    code_to_insert.insert_after_line_2x(c_code, "int main() {", parametres_window, code_to_insert.code_create_window_fullscreen)
                    code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                else :
                    code_to_insert.remove_lines_after_keyword(c_code, "   //Parametres window", 14)
                    code_to_insert.insert_after_line_2x(c_code, "int main() {", parametres_window, code_to_insert.code_create_window_fullscreen)
                    code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
            else :
                parametres_window = code_to_insert.get_parametres_window(x, y, r, g, b)
                if code_to_insert.check_comment_in_code(c_code, "//Create window") == 0:
                    code_to_insert.insert_after_line_2x(c_code, "int main() {", parametres_window, code_to_insert.code_create_window_modify)
                    code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
                else :
                    code_to_insert.remove_lines_after_keyword(c_code, "// Parametres window", 14)
                    code_to_insert.insert_after_line_2x(c_code, "int main() {", parametres_window, code_to_insert.code_create_window_modify)
                    code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
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

    from code_to_insert import insert_code_if_comment_not_present, code_staywindow_open
    insert_code_if_comment_not_present(c_code, code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
        
    c_code.append("    return 0;")
    c_code.append("}")  # Fin de la fonction main
 
        # Retourner le code complet C avec le main inclus
    return "\n".join(c_code)
