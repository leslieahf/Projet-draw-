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
    c_code.append("")

    c_code.append("""
    void drawCarre(SDL_Renderer* renderer, int x, int y, int taille, int r, int g, int b) {
        SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du carré
        SDL_Rect rect = {x, y, taille, taille};  // Définir les dimensions et la position du carré
        SDL_RenderFillRect(renderer, &rect); // Dessiner le carré
    }
    """)
    c_code.append("""
    void dessinerRectangle(SDL_Renderer* renderer, int x, int y, int largeur, int hauteur, int r, int g, int b) {
    SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du rectangle
    SDL_Rect rect = {x, y, largeur, hauteur};       // Définir la position et la taille du rectangle
    SDL_RenderFillRect(renderer, &rect);              // Dessiner le rectangle
    }
    """)
    
    c_code.append("int main() {")  # Début de la fonction main

    for i, line in enumerate(lines):
        line = line.strip()  # Supprimer les espaces autour de la ligne
        # Si c'est une fonction ou une condition, on ne modifie pas le point-virgule

        if line.startswith("function") or line.startswith("if") or line.startswith("else"):
            c_code.append(f"    {line}")  # Ajouter avec une indentation de 4 espaces
            # Si c'est une affectation ou une déclaration, on ajoute un point-virgule pour C
       
        elif line.startswith("draw"): 
            # Extraire les informations entre les parenthèses
            arguments = line[line.find("(") + 1 : line.rfind(")")]

            # Diviser les arguments intelligemment en tenant compte des guillemets
            def split_arguments(argument_string):
                """Divise une chaîne d'arguments en morceaux tout en respectant les guillemets et les virgules."""
                args = []
                current = ""
                in_quotes = False  # Flag pour savoir si on est à l'intérieur de guillemets
                for char in argument_string:
                    if char == "," and not in_quotes:
                        # Si on rencontre une virgule hors des guillemets, on termine un argument
                        args.append(current.strip())
                        current = ""
                    else:
                        current += char
                        if char == "\"":
                            in_quotes = not in_quotes  # Toggle l'état des guillemets
                # Ajouter le dernier argument
                if current:
                    args.append(current.strip())
                return args
            # Diviser les arguments
            raw_args = split_arguments(arguments)
            # Traiter chaque argument
            shape = raw_args[0].strip()  # Premier argument : le type de forme (carre)
            # Deuxième argument : couleur RGB (chaîne sous forme "255,255,255")
            couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
            couleur = tuple(map(int, couleur_raw.split(",")))  # Convertir en tuple d'entiers
            # Troisième argument : coordonnées (x, y) sous forme "10,10"
            coordonnees_raw = raw_args[2].strip("\"")  # Enlever les guillemets autour des coordonnées
            coordonnees = tuple(map(int, coordonnees_raw.split(",")))
            # Quatrième argument : taille
            taille = int(raw_args[3])
            # Assigner les sous-valeurs
            x, y = coordonnees  # Extraire les coordonnées
            r, g, b = couleur   # Extraire les couleurs RGB

            if shape == "carre" in line:
                c_code.append("SDL_Init(SDL_INIT_VIDEO);")
                c_code.append("SDL_Window* window = SDL_CreateWindow(\"Afficher un carré\", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);")# Création de la fenêtre
                c_code.append("SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);")# Création du renderer
                c_code.append("SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);")# Couleur de fond (noir)
                c_code.append("SDL_RenderClear(renderer);")
                c_code.append(f"int x = {x};        // Coordonnée x")
                c_code.append(f"int y = {y};        // Coordonnée y")
                c_code.append(f"int taille = {taille};   // Taille du carré")
                c_code.append(f"int r = {r};        // Rouge")
                c_code.append(f"int g = {g};        // Vert")
                c_code.append(f"int b = {b};        // Bleu")
                c_code.append("drawCarre(renderer, x, y, taille, r, g, b);")# Appel de la fonction pour dessiner un carré
                c_code.append("SDL_RenderPresent(renderer);")# Affichage du rendu
                c_code.append("SDL_Delay(5000);")# Pause pour visualiser le carré (5 secondes)
                c_code.append("SDL_DestroyRenderer(renderer);")# Libération des ressources
                c_code.append("SDL_DestroyWindow(window);")
                c_code.append("SDL_Quit();")
            elif shape == 'rectangle' in line: 
                c_code.append('SDL_Init(SDL_INIT_VIDEO);  // Initialiser SDL')
                c_code.append('SDL_Window* window = SDL_CreateWindow("Dessiner un rectangle", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);')
                c_code.append('SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);')
                c_code.append(f"int x = {x};        // Coordonnée x")
                c_code.append(f"int y = {y};        // Coordonnée y")
                c_code.append(f"int taille = {taille};   // Taille du carré")
                c_code.append(f"int r = {r};        // Rouge")
                c_code.append(f"int g = {g};        // Vert")
                c_code.append(f"int b = {b};        // Bleu")
                # Convertir la taille en largeur et hauteur
                c_code.append('int largeur = (int)(taille * 0.6);   // 60% de la taille pour la largeur')
                c_code.append('int hauteur = (int)(taille * 0.4);   // 40% de la taille pour la hauteur')
                c_code.append('SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);  // Couleur de fond (noir)')
                c_code.append('SDL_RenderClear(renderer);  // Effacer l\'écran')
                c_code.append('dessinerRectangle(renderer, 200, 150, largeur, hauteur, r, g, b);')# Dessiner le rectangle
                c_code.append('SDL_RenderPresent(renderer);  // Afficher le rendu')
                c_code.append('SDL_Delay(5000);  // Attente 5 secondes avant de fermer')
                # Libérer les ressources
                c_code.append('SDL_DestroyRenderer(renderer);')
                c_code.append('SDL_DestroyWindow(window);')
                c_code.append('SDL_Quit();')

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
