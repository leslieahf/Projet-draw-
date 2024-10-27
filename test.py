import re

code = """
repeat 5 {
    create_cursor("blue", (100, 200))
    move_cursor(45)
    draw()
}
"""

def translate_to_c(code):
    translated_code = ""
    # Détecte une boucle `repeat`
    repeat_pattern = r"repeat (\d+) {([\s\S]+?)}"
    matches = re.finditer(repeat_pattern, code)
    
    for match in matches:
        count = int(match.group(1))
        instructions = match.group(2).strip().splitlines()
        
        # Traduction en C
        translated_code += f"for (int i = 0; i < {count}; i++) {{\n"
        
        for instruction in instructions:
            instruction = instruction.strip()
            
            if instruction.startswith("create_cursor"):
                # Utilisation de regex afin d'extraire les paramètre de la fonctions
                cursor_match = re.match(r'create_cursor\("(\w+)",\s*\((\d+),\s*(\d+)\)\)', instruction)
                if cursor_match:
                    color = cursor_match.group(1)
                    x_pos = cursor_match.group(2)
                    y_pos = cursor_match.group(3)
                    translated_code += f'    create_cursor("{color}", {x_pos}, {y_pos});\n'
                    
            elif instruction.startswith("move_cursor"):
                move_match = re.match(r'move_cursor\((\d+)\)', instruction)
                if move_match:
                    angle = move_match.group(1)
                    translated_code += f'    move_cursor({angle});\n'
            
            elif instruction.startswith("draw"):
                translated_code += "    draw();\n"
        
        translated_code += "}\n"
    
    return translated_code

# Traduction du code
translated_code = translate_to_c(code)
print(translated_code)
