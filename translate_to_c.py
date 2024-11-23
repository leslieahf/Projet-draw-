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
    c_code = ["int main() {"]  # Début de la fonction main

    for i, line in enumerate(lines):
        line = line.strip()  # Supprimer les espaces autour de la ligne

        # Si c'est une fonction ou une condition, on ne modifie pas le point-virgule
        if line.startswith("function") or line.startswith("if") or line.startswith("else"):
            c_code.append(f"    {line}")  # Ajouter avec une indentation de 4 espaces
        # Si c'est une affectation ou une déclaration, on ajoute un point-virgule pour C
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
        else:
            c_code.append(f"    {line}")  # Laisser la ligne telle quelle, avec indentation

    c_code.append("    return 0;")
    c_code.append("}")  # Fin de la fonction main

    # Retourner le code complet C avec le main inclus
    return "\n".join(c_code)
