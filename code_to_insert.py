code_drawCarre = [
    "",
    "void drawCarre(SDL_Renderer* renderer, int x, int y, int taille, int r, int g, int b) {",
    "    SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du carré",
    "    SDL_Rect rect = {x, y, taille, taille};  // Définir les dimensions et la position du carré",
    "    SDL_RenderFillRect(renderer, &rect);  // Dessiner le carré",
    "}"
]

code_drawRectangle = [
    "",
    "void drawRectangle(SDL_Renderer* renderer, int x, int y, int largeur, int hauteur, int r, int g, int b) {",
    "    SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du rectangle",
    "    SDL_Rect rect = {x, y, largeur, hauteur};       // Définir la position et la taille du rectangle",
    "    SDL_RenderFillRect(renderer, &rect);            // Dessiner le rectangle",
    "}"
]

code_drawCercle = [
    "",
    "void drawCercle(SDL_Renderer* renderer, int cx, int cy, int rayon, int r, int g, int b) {",
    "    SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du cercle",
    "    for (int y = -rayon; y <= rayon; y++) {",
    "        for (int x = -rayon; x <= rayon; x++) {",
    "            if (x * x + y * y <= rayon * rayon) {  // Équation d'un cercle : x² + y² ≤ r²",
    "                SDL_RenderDrawPoint(renderer, cx + x, cy + y);",
    "            }",
    "        }",
    "    }",
    "}"
]

code_drawTriangle = [
    "void drawTriangle(SDL_Renderer* renderer, int x1, int y1, int x2, int y2, int x3, int y3, int r, int g, int b) {",
    "SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur du triangle",
    "SDL_RenderDrawLine(renderer, x1, y1, x2, y2);    // Ligne entre le premier et le deuxième point",
    "SDL_RenderDrawLine(renderer, x2, y2, x3, y3);    // Ligne entre le deuxième et le troisième point",
    "SDL_RenderDrawLine(renderer, x3, y3, x1, y1);  // Ligne entre le troisième et le premier point",
"}",

]

code_drawPolygon =[
   " void drawPolygon(SDL_Renderer* renderer, int cx, int cy, int rayon, int sides, int r, int g, int b) {",
    "SDL_SetRenderDrawColor(renderer, r, g, b, 255);",
    "double angleStep = 2 * M_PI / sides;  // Angle entre chaque sommet",
    "int x1 = cx + rayon * cos(0);        // Premier sommet",
    "int y1 = cy + rayon * sin(0);",

    "for (int i = 1; i <= sides; i++) {",
        "int x2 = cx + rayon * cos(i * angleStep);  // Calcul du prochain sommet",
        "int y2 = cy + rayon * sin(i * angleStep);",
        "SDL_RenderDrawLine(renderer, x1, y1, x2, y2);  // Dessiner une ligne entre deux sommets",
        "x1 = x2;",
        "y1 = y2;",
    "}"
"}"
]

code_drawLosange = [
    "void drawLosange(SDL_Renderer* renderer, int cx, int cy, int largeur, int hauteur, int r, int g, int b) {",
    "SDL_SetRenderDrawColor(renderer, r, g, b, 255);",
    "int x1 = cx;               // Point haut",
    "int y1 = cy - hauteur / 2;",
    "int x2 = cx + largeur / 2; // Point droit",
    "int y2 = cy;",
    "int x3 = cx;               // Point bas",
    "int y3 = cy + hauteur / 2;",
    "int x4 = cx - largeur / 2; // Point gauche",
    "int y4 = cy;",

    "// Dessiner les 4 côtés",
    "SDL_RenderDrawLine(renderer, x1, y1, x2, y2);",
    "SDL_RenderDrawLine(renderer, x2, y2, x3, y3);",
    "SDL_RenderDrawLine(renderer, x3, y3, x4, y4);",
    "SDL_RenderDrawLine(renderer, x4, y4, x1, y1);",
"}",

]

code_drawTrapeze =[
    "void drawTrapeze(SDL_Renderer* renderer, int x, int y, int largeurHaut, int largeurBas, int hauteur, int r, int g, int b) {",
    "SDL_SetRenderDrawColor(renderer, r, g, b, 255);",
    "int x1 = x;                            // Coin supérieur gauche",
    "int y1 = y;",
    "int x2 = x + largeurHaut;              // Coin supérieur droit",
    "int y2 = y;",
    "int x3 = x + (largeurBas - largeurHaut) / 2 + largeurBas; // Coin inférieur droit",
    "int y3 = y + hauteur;",
    "int x4 = x - (largeurBas - largeurHaut) / 2;              // Coin inférieur gauche",
    "int y4 = y + hauteur;",

    "// Dessiner les côtés",
    "SDL_RenderDrawLine(renderer, x1, y1, x2, y2);",
    "SDL_RenderDrawLine(renderer, x2, y2, x3, y3);",
    "SDL_RenderDrawLine(renderer, x3, y3, x4, y4);",
    "SDL_RenderDrawLine(renderer, x4, y4, x1, y1);",
"}",

]

code_drawLine = [
    "",
   "void drawLine(SDL_Renderer* renderer, int x1, int y1, int x2, int y2, int r, int g, int b) {",
    "SDL_SetRenderDrawColor(renderer, r, g, b, 255);  // Définir la couleur de la ligne",
    "SDL_RenderDrawLine(renderer, x1, y1, x2, y2);   // Dessiner la ligne de (x1, y1) à (x2, y2)",
"}",
]

code_create_window = [
    "//Create window",
    "SDL_Init(SDL_INIT_VIDEO);",  # Initialiser SDL
    "SDL_Window* window = SDL_CreateWindow(\"Afficher un carré\", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);",  # Création de la fenêtre
    "SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);",  # Création du renderer
    "SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);",  # Couleur de fond (noir)
    "SDL_RenderClear(renderer);",  # Effacer l'écran avec la couleur de fond
    ""
]

code_create_window_modify = [
    "//Create window",
    "SDL_Init(SDL_INIT_VIDEO);",  # Initialiser SDL
    "SDL_Window* window = SDL_CreateWindow(\"Afficher un dessin\", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, x_window , y_window , SDL_WINDOW_SHOWN);",  # Création de la fenêtre
    "SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);",  # Création du renderer
    "SDL_SetRenderDrawColor(renderer, r_window , g_window , b_window , 255);",  # Couleur de fond (noir)
    "SDL_RenderClear(renderer);",  # Effacer l'écran avec la couleur de fond
    ""
]

code_create_window_fullscreen = [
    "//Create window",
    "SDL_Init(SDL_INIT_VIDEO);",  # Initialiser SDL
    "SDL_Window* window = SDL_CreateWindow(\"Afficher un dessin\", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 0, 0, SDL_WINDOW_FULLSCREEN);",  # Création de la fenêtre en plein écran
    "SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);",  # Création du renderer
    "SDL_SetRenderDrawColor(renderer, r_window, g_window, b_window, 255);",
    "SDL_RenderClear(renderer);",  # Effacer l'écran avec la couleur de fond
    ""
]
 

code_staywindow_open = [
    "// Garder la fenêtre ouverte en permanence avec une boucle événementielle",
    "SDL_RenderPresent(renderer);",  # Afficher le rendu une seule fois avant la boucle
    "SDL_Event event;  // Variable pour stocker les événements",
    "int running = 1;  // Flag pour contrôler la boucle",
    "while (running) {",
    "    while (SDL_PollEvent(&event)) {",
    "        // Gérer les différents événements",
    "        if (event.type == SDL_QUIT) {",
    "            // Si l'utilisateur demande de fermer la fenêtre",
    "            running = 0;  // Sortir de la boucle",
    "        }",
    "    }",
    "    SDL_Delay(16);  // Limiter le framerate à environ 60 FPS",
    "}",
   
]



def get_parametres_carre(x, y, taille, r, g, b):
    return [
        "{"
        "   // Parametres carre",    
        f"  int x_carre = {x};        // Coordonnée x",
        f"  int y_carre = {y};        // Coordonnée y",
        f"  int taille_carre = {taille};   // Taille du carré",
        f"  int r_carre = {r};        // Rouge",
        f"  int g_carre = {g};        // Vert",
        f"  int b_carre = {b};        // Bleu",
        "   drawCarre(renderer, x_carre, y_carre, taille_carre, r_carre, g_carre, b_carre);",  # Appel à la fonction pour dessiner
        "   // Fin parametres carre",
        "}"
        ""
    ]

def get_parametres_rectangle(x, y, taille, r, g, b):
    return [
        "{",
        "   // Parametres rectangle",
        f"   int x_rectangle = {x};        // Coordonnée x",
        f"   int y_rectangle = {y};        // Coordonnée y",
        f"   int taille_rectangle = {taille};   // Taille du rectangle",
        f"   int r_rectangle = {r};        // Rouge",
        f"   int g_rectangle = {g};        // Vert",
        f"   int b_rectangle = {b};        // Bleu",
        "   int largeur = (int)(taille_rectangle * 0.6);   // 60% de la taille pour la largeur",
        "   int hauteur = (int)(taille_rectangle * 0.4);   // 40% de la taille pour la hauteur",
        "   drawRectangle(renderer, x_rectangle, y_rectangle, largeur, hauteur, r_rectangle, g_rectangle, b_rectangle);",  # Dessiner le rectangle
        "   // Fin parametres rectangle",
        "}"
    ]

def get_parametres_cercle(x, y, taille, r, g, b):
    return [
        "{",
        "   // Parametres cercle",
        f"   int x_cercle = {x};        // Coordonnée x",
        f"   int y_cercle = {y};        // Coordonnée y",
        f"   int taille_cercle = {taille};   // Taille du cercle",
        f"   int r_cercle = {r};        // Rouge",
        f"   int g_cercle = {g};        // Vert",
        f"   int b_cercle = {b};        // Bleu",
        "   drawCercle(renderer, x_cercle, y_cercle, taille_cercle, r_cercle, g_cercle, b_cercle);  // Cercle au centre",
        "   // Fin parametres cercle",
        "}"
    ]

def get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b):
    return [
        "{",
        "   // Parametres triangle",
        f"   int x1_triangle = {x1};    // Premier point (x1, y1)",
        f"   int y1_triangle = {y1};",
        f"   int x2_triangle = {x2};    // Deuxième point (x2, y2)",
        f"   int y2_triangle = {y2};",
        f"   int x3_triangle = {x3};    // Troisième point (x3, y3)",
        f"   int y3_triangle = {y3};",
        f"   int r_triangle = {r};      // Rouge",
        f"   int g_triangle = {g};      // Vert",
        f"   int b_triangle = {b};      // Bleu",
        "   drawTriangle(renderer, x1_triangle, y1_triangle, x2_triangle, y2_triangle, x3_triangle, y3_triangle, r_triangle, g_triangle, b_triangle);",
        "   // Fin parametres triangle",
        "}"
    ]

def get_parametres_polygone(cx, cy, rayon, sides, r, g, b):
    nom = {5: "pentagone", 6: "hexagone", 8: "octogone"}.get(sides, "polygone")
    return [
        "{",
        f"   // Parametres {nom}",
        f"   int cx_{nom} = {cx};       // Centre X",
        f"   int cy_{nom} = {cy};       // Centre Y",
        f"   int rayon_{nom} = {rayon}; // Rayon du {nom}",
        f"   int r_{nom} = {r};         // Rouge",
        f"   int g_{nom} = {g};         // Vert",
        f"   int b_{nom} = {b};         // Bleu",
        f"   drawPolygon(renderer, cx_{nom}, cy_{nom}, rayon_{nom}, {sides}, r_{nom}, g_{nom}, b_{nom});",
        f"   // Fin parametres {nom}",
        "}"
    ]

def get_parametres_losange(cx, cy, largeur, hauteur, r, g, b):
    return [
        "{",
        "   // Parametres losange",
        f"   int cx_losange = {cx};        // Centre X",
        f"   int cy_losange = {cy};        // Centre Y",
        f"   int largeur_losange = {largeur};   // Largeur du losange",
        f"   int hauteur_losange = {hauteur};   // Hauteur du losange",
        f"   int r_losange = {r};          // Rouge",
        f"   int g_losange = {g};          // Vert",
        f"   int b_losange = {b};          // Bleu",
        "   drawLosange(renderer, cx_losange, cy_losange, largeur_losange, hauteur_losange, r_losange, g_losange, b_losange);",
        "   // Fin parametres losange",
        "}"
    ]

def get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b):
    return [
        "{",
        "   // Parametres trapèze",
        f"   int x_trapeze = {x};             // Coordonnée X du sommet supérieur gauche",
        f"   int y_trapeze = {y};             // Coordonnée Y du sommet supérieur gauche",
        f"   int largeur_haut_trapeze = {largeur_haut};  // Largeur du sommet supérieur",
        f"   int largeur_bas_trapeze = {largeur_bas};    // Largeur du sommet inférieur",
        f"   int hauteur_trapeze = {hauteur};           // Hauteur du trapèze",
        f"   int r_trapeze = {r};            // Rouge",
        f"   int g_trapeze = {g};            // Vert",
        f"   int b_trapeze = {b};            // Bleu",
        "   drawTrapeze(renderer, x_trapeze, y_trapeze, largeur_haut_trapeze, largeur_bas_trapeze, hauteur_trapeze, r_trapeze, g_trapeze, b_trapeze);",
        "   // Fin parametres trapèze",
        "}"
    ]

def get_parametres_line(x1, y1, x2, y2,r, g, b):
    return [
        "{",
        "   // Parametres ligne",
        f"   int x1_line = {x1};        // Coordonnée x1 (départ)",
        f"   int y1_line = {y1};        // Coordonnée y1 (départ)",
        f"   int x2_line = {x2};        // Coordonnée x2 (fin)",
        f"   int y2_line = {y2};        // Coordonnée y2 (fin)",
        f"   int r_line = {r};          // Rouge",
        f"   int g_line = {g};          // Vert",
        f"   int b_line = {b};          // Bleu",
        "   drawLine(renderer, x1_line, y1_line, x2_line, y2_line,r_line, g_line, b_line);",  # Appel à la fonction pour dessiner la ligne
        "   // Fin parametres ligne",
        "}"
    ]
def extract_window_params(arguments):
    raw_args = split_arguments(arguments)
    coordonnees_raw = raw_args[0].strip("\"")  # Enlever les guillemets autour du premier argument
    coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en tuple d'entiers
    x, y = coordonnees  # Extraire les coordonnées
    couleur_raw = raw_args[1].strip("\"")  # Enlever les guillemets autour de la couleur
    couleur = tuple(map(int, map(str.strip, couleur_raw.split(","))))  # Convertir en tuple d'entiers
    r, g, b = couleur  # Extraire les couleurs RGB
 
    return coordonnees, x, y, r, g, b
def get_parametres_window(x, y, r, g, b):
    return [
        "   //Parametres window",    
        f"  int x_window = {x};        // Coordonnée x",
        f"  int y_window = {y};        // Coordonnée y",
        f"  int r_window = {r};        // Rouge",
        f"  int g_window = {g};        // Vert",
        f"  int b_window = {b};        // Bleu",
        "   // Fin parametres window",
        ""
    ]
def remove_lines_after_keyword(c_code, keyword, nb_lines_to_remove):
    if keyword in c_code:
        start_index = c_code.index(keyword)
        end_index = start_index + nb_lines_to_remove
        del c_code[start_index:end_index]
    else :
        c_code.append("frere c'est pas supprime chacal")
    return c_code
def insert_code_before_first_occurrence(c_code, target_line, code_to_add):
    for i, line in enumerate(c_code):
        if target_line in line:
            # Si code_to_add est une liste, insérer tous les éléments d'un coup
            if isinstance(code_to_add, list):
                c_code[i:i] = code_to_add  # Ajout tout en une seule opération
            else:
                # Si c'est une chaîne, on l'insère directement
                c_code.insert(i, code_to_add)
            break  # Arrêter après avoir inséré
    return c_code




def insert_after_line(c_code, target_line, code_to_insert):
        # Trouver l'index de la ligne cible
        index = next((i for i, line in enumerate(c_code) if line == target_line), -1)

        if index != -1:  # Si la ligne cible est trouvée
            # Ajouter le code à insérer juste après cette ligne
            c_code[index+1:index+1] = code_to_insert
        else:
            print("erreur")

def insert_after_previous_line(c_code, code_to_insert):
    """
    Insère un bloc de code juste après la dernière ligne du code présent.

    Args:
        c_code (list of str): Liste des lignes du code C.
        code_to_insert (list of str): Bloc de code à insérer sous forme de liste de lignes.

    Returns:
        None
    """
    # Ajouter le code à insérer juste à la fin de la liste des lignes existantes
    c_code.extend(code_to_insert)
    
def insert_code_if_comment_not_present(c_code, code_to_insert, comment_variable):
    # Vérifier si le comment_variable est déjà présent dans c_code
    comment_present = False
    for line in c_code:
        if comment_variable in line:
            comment_present = True
            break
    
    # Si le comment_variable n'est pas présent, ajouter le code
    if not comment_present:
        c_code.extend(code_to_insert)

def check_comment_in_code(c_code, comment_variable):
    for line in c_code:
        if comment_variable in line:
            return 1  # Si le commentaire est trouvé, retourne 1
    return 0  # Si le commentaire n'est pas trouvé, retourne 0

def insert_code_after_last_occurrence(c_code, target_line, code_to_add):
    # Rechercher la dernière occurrence du mot de recherche
    last_index = -1
    for i, line in enumerate(c_code):
        if target_line in line:
            last_index = i  # Sauvegarder l'indice de la dernière occurrence
    
    # Si on n'a pas trouvé de dernière occurrence, afficher un message d'erreur
    if last_index == -1:
        print(f"Erreur : '{target_line}' n'a pas été trouvé dans le code.")
        return

    # Si on a trouvé la dernière occurrence, on ajoute le code après cette ligne
    c_code.insert(last_index + 1, code_to_add)
    print(f"Code ajouté après la ligne : {last_index}")
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
def insert_after_line_2x(c_code, target_line, code_to_insert_1, code_to_insert_2):
    # Trouver l'index de la ligne cible
    index = next((i for i, line in enumerate(c_code) if line == target_line), -1)
 
    if index != -1:
        c_code[index + 1:index + 1] = code_to_insert_1
    
        new_index = index + 1 + len(code_to_insert_1)
        c_code[new_index:new_index] = code_to_insert_2
    else:
        print("Erreur : Ligne cible introuvable")
    return c_code
