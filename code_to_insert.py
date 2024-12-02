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

code_create_window = [
    "//Create window",
    "SDL_Init(SDL_INIT_VIDEO);",  # Initialiser SDL
    "SDL_Window* window = SDL_CreateWindow(\"Afficher un carré\", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);",  # Création de la fenêtre
    "SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);",  # Création du renderer
    "SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);",  # Couleur de fond (noir)
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
    "// Libérer les ressources avant de quitter",
    "SDL_DestroyRenderer(renderer);",
    "SDL_DestroyWindow(window);",
    "SDL_Quit();"
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

def insert_after_line(c_code, target_line, code_to_insert):
        # Trouver l'index de la ligne cible
        index = next((i for i, line in enumerate(c_code) if line == target_line), -1)

        if index != -1:  # Si la ligne cible est trouvée
            # Ajouter le code à insérer juste après cette ligne
            c_code[index+1:index+1] = code_to_insert
        else:
            print("erreur")

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
    
    # Si on a trouvé la dernière occurrence, on ajoute le code après cette ligne
    if last_index != -1:
        c_code.insert(last_index + 1, code_to_add)
