 
import re
import code_to_insert
 
def parse_or_variable(arg):
    """
    If arg is a literal number (e.g., "100"), return int(arg).
    If it's a literal float (e.g., "3.14"), return float(arg).
    Otherwise, it's a variable name => return the string as-is.
    """
    if re.match(r'^-?\d+$', arg):
        return int(arg)
    if re.match(r'^-?\d+\.\d+$', arg):
        return float(arg)
    return arg  # identifiant de variable ou autre chaîne brute
 
def get_printf_format_and_cast(variable, symbol_table):
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
    Handles function declarations via 'func name(...) { ... }'.
    """
    symbol_table = {}
 
     # First, perform basic replacements across the entire code
    draw_code = draw_code.replace(" <- ", " = ")\
                         .replace(" eq ", " == ")\
                         .replace(" neq ", " != ")\
                         .replace("and", "&&")\
                         .replace(" or ", " || ")\
                         .replace("true", "1")\
                         .replace("false", "0")\
                         .replace("infs", "<")\
                         .replace("inf", "<=")\
                         .replace(">", "sups")\
                         .replace(">=", "sup")
 
    # Split into lines
    lines = draw_code.split("\n")
    
    # Code buffers:
    global_functions = []
    functions_code = []  # Store translated functions
    main_code = []       # Store the translation of what goes into main()
    window_created = [False]
    # Variable to track if we are “inside” a function body
    in_func = False
    current_func_name = None
    current_func_buffer = []  # To accumulate the function body
 
    # Small utility function for translating a print
    def translate_print(match,symbol_table):
        expr = match.group(1).strip()
    
   # Simple detection
        if re.search(r'[+\-*/]', expr):
        # It's a small expression: print(a+b)
        # Assume everything as int for this example
            return f'printf("%d\\n", {expr});'
        else:
         # Single token: variable or literal
            format_specifier, casted_variable = get_printf_format_and_cast(expr, symbol_table)
            return f'printf("{format_specifier}\\n", {casted_variable});'
 
    for line in lines:
        original_line = line.strip()
        
        # Detect the start of a function: e.g., "func myFunction( x, y ) {"
        match_func_start = re.match(r'^func\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*\{', original_line)
        if match_func_start:
            # We enter a function
            in_func = True
            current_func_name = match_func_start.group(1)
            func_args = match_func_start.group(2).strip()

            return_type = "void"
            if "return 0" in draw_code:  
                return_type = "int"

            if func_args == "":
                functions_code.append(f"{return_type} {current_func_name}(SDL_Renderer* renderer) {{")
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
                functions_code.append(f"{return_type} {current_func_name}(SDL_Renderer* renderer, {c_args}) {{")

        
            current_func_buffer = []
            continue
 
        # Detect the end of a function: a line containing only "}"
        if in_func and original_line == "}":
            # Close the function
            in_func = False
            # Add all translated lines accumulated
            for func_line in current_func_buffer:
                # Check if the line contains a return without a semicolon
                if func_line.strip().startswith("return") and not func_line.strip().endswith(";"):
                    func_line += ";"  
                functions_code.append("    " + func_line)
             # Close the function
            functions_code.append("}\n")
            current_func_buffer = []
            current_func_name = None
            continue
 
          # If inside a function, accumulate lines
        if in_func:
            # Here, reuse the existing translation logic,
            # but apply it to current_func_buffer instead of main_code.
            
            translated_line = line_translator(line, translate_print,window_created,symbol_table,global_functions)
            # Store the result
            current_func_buffer.extend(translated_line)
        
        else:
            # Outside of a function: apply the same translation logic
            translated_line = line_translator(line,translate_print,window_created,symbol_table,global_functions)
            main_code.extend(translated_line)
 
 
     # Now that we’ve separated function code and main() code,
    # assemble the final code
    c_code = []
     # Standard includes
    c_code.append("#include <SDL2/SDL.h>")
    c_code.append("#include <stdio.h>")
    c_code.append("#include <stdbool.h>")
    c_code.append("#include <SDL2/SDL_ttf.h>")
    c_code.append("#include <math.h>\n")
    c_code.append("bool window_created = false;\n")

 
    c_code.extend(global_functions)
    # Add functions before the main
    c_code.extend(functions_code)
 
    # Start main
    c_code.append("int main() {\n")
    if not window_created[0]:
                c_code.append("// Création de la fenêtre")
                c_code.extend(code_to_insert.code_create_window)
                c_code.append("    window_created = true;")
                window_created[0] = True 
    # Add main code with indentation
    for line in main_code:
        c_code.append("    " + line)
   # End
    
    code_to_insert.insert_code_if_comment_not_present(c_code, code_to_insert.code_staywindow_open, "// Garder la fenêtre ouverte en permanence avec une boucle événementielle")
    c_code.append("    return 0;")
    c_code.append("}\n")
    return "\n".join(c_code)
 
 
def line_translator(line,translate_print,window_created,symbol_table,global_functions):
    line = line.strip()
    result_lines = []
 
   # Example: if the line starts with "freedraw", handle it
    # Here, I use excerpts from your existing code and simplify.
    if line.startswith("freedraw"):
        result_lines.append("// Freedraw: insertion du code_instructions_freedraw")
        global_functions.extend(code_to_insert.code_instructions_freedraw)
        result_lines.extend(code_to_insert.code_mainProgram_freedraw)
    elif line.startswith("draw"):
        # Extract the information inside the parentheses
            arguments = line[line.find("(") + 1: line.rfind(")")]
            # Process each argument
            raw_args = code_to_insert.split_arguments(arguments)
            # Traiter chaque argument
            shape = raw_args[0].strip()  # First argument: type of shape 
            # Second argument: RGB color (string in the form "255, 255, 255")
            couleur_raw = raw_args[1].strip("\"")
            resolved_couleur = []

            for part in couleur_raw.split(","):
                part = part.strip()
                if re.match(r'^[a-zA-Z_]\w*$', part): # Check if it's a variable
                    if part not in symbol_table:
                        raise ValueError(f"Variable '{part}' not declared.")
                    resolved_couleur.append(symbol_table[part]["value"])  # Retrieve the variable's value
                elif re.match(r'^-?\d+$', part): # Check if it's an integer
                    resolved_couleur.append(int(part))
                else:
                    raise ValueError(f"Invalid RGB component: '{part}'. Expected a variable or an integer.")

             # Convert the list to a tuple
            couleur = tuple(resolved_couleur)
            r, g, b = couleur   # Extract the RGB colors
        
            
            if "carre" in line:
                 # Third argument: coordinates (x, y) in the form "10,10"
                coordonnees_raw = raw_args[2].strip("\"")  
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(",")))) # Convert to a tuple of integers
                taille = parse_or_variable(raw_args[3])
                x, y = coordonnees  # Extract the coordinates
                if not code_to_insert.check_comment_in_code(global_functions, "void drawCarre"):
                    global_functions.append("// Définition de la fonction drawCarre")
                    global_functions.extend(code_to_insert.code_drawCarre)
                parametres_carre = code_to_insert.get_parametres_carre(x, y, taille, r, g, b)
                result_lines.append("// Paramètres pour le carré :")
                result_lines.extend(parametres_carre)
            elif "rectangle" in line:
               
                coordonnees_raw = raw_args[2].strip("\"") 
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  
                hauteur = parse_or_variable((raw_args[3]))
                largeur = parse_or_variable(raw_args[4])
                x, y = coordonnees  
                if not code_to_insert.check_comment_in_code(global_functions, "void drawRectangle"):
                    global_functions.append("// Définition de la fonction drawRectangle")
                    global_functions.extend(code_to_insert.code_drawRectangle)
                parametres_rectangle = code_to_insert.get_parametres_rectangle(x, y, hauteur ,largeur, r, g, b)
                result_lines.append("// Paramètres pour le rectangle :")
                result_lines.extend(parametres_rectangle)
            elif "cercle" in line:
                
                coordonnees_raw = raw_args[2].strip("\"") 
                coordonnees = tuple(coord.strip() for coord in coordonnees_raw.split(","))  
                x, y = coordonnees  
                if not code_to_insert.check_comment_in_code(global_functions, "void drawCercle"):
                    global_functions.append("// Définition de la fonction drawCercle")
                    global_functions.extend(code_to_insert.code_drawCercle)
                parametres_cercle = code_to_insert.get_parametres_cercle(x, y, taille, r, g, b)
                result_lines.append("// Paramètres pour le cercle :")
                result_lines.extend(parametres_cercle)
            elif "triangle" in line:
                
                coordonnees_raw = raw_args[2].strip("\"") 
                coordonnees = list(map(int, map(str.strip, coordonnees_raw.split(","))))  # Convertir en liste d'entiers
                if len(coordonnees) != 6:
                    raise ValueError("Un triangle nécessite exactement 6 coordonnées (x1, y1, x2, y2, x3, y3).")
                x1, y1, x2, y2, x3, y3 = coordonnees 
                
                
                if not code_to_insert.check_comment_in_code(global_functions, "void drawTriangle"):
                    global_functions.append("// Définition de la fonction drawTriangle")
                    global_functions.extend(code_to_insert.code_drawTriangle)
                parametres_triangle = code_to_insert.get_parametres_triangle(x1, y1, x2, y2, x3, y3, r, g, b)
                result_lines.append("// Paramètres pour le triangle:")
                result_lines.extend(parametres_triangle)
            elif "polygon" in line:
                
                coordonnees_raw = raw_args[2].strip("\"") 
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  
                taille = parse_or_variable(raw_args[3])
                x, y = coordonnees 
                types_polygon = parse_or_variable(raw_args[4])
                if not code_to_insert.check_comment_in_code(global_functions, "void drawPolygon"):
                    global_functions.append("// Définition de la fonction drawPolygon")
                    global_functions.extend(code_to_insert.code_drawPolygon)
                parametres_polygon = code_to_insert.get_parametres_polygone(x, y, taille,types_polygon, r, g, b)
                result_lines.append("// Paramètres pour le polygone:")
                result_lines.extend(parametres_polygon)
            elif "losange" in line:
                
                coordonnees_raw = raw_args[2].strip("\"") 
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  
                x, y = coordonnees 
                largeur=parse_or_variable(raw_args[3])
                hauteur=parse_or_variable(raw_args[4])
                if not code_to_insert.check_comment_in_code(global_functions, "void drawLosange"):
                    global_functions.append("// Définition de la fonction drawLosange")
                    global_functions.extend(code_to_insert.code_drawLosange)
                parametres_losange = code_to_insert.get_parametres_losange(x, y, largeur,hauteur, r, g, b)
                result_lines.append("// Paramètres pour le losange:")
                result_lines.extend(parametres_losange)
            elif "trapeze" in line:
              
                coordonnees_raw = raw_args[2].strip("\"")  
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(","))))  
                x, y = coordonnees  
            
                largeur_haut = parse_or_variable(raw_args[3])
                largeur_bas = parse_or_variable(raw_args[4])
                hauteur = parse_or_variable(raw_args[5])
                r, g, b = couleur  
                if not code_to_insert.check_comment_in_code(global_functions, "void drawTrapeze"):
                    global_functions.append("// Définition de la fonction drawTrapeze")
                    global_functions.extend(code_to_insert.code_drawTrapeze)
                parametres_trapeze = code_to_insert.get_parametres_trapeze(x, y, largeur_haut, largeur_bas, hauteur, r, g, b)
                result_lines.append("// Paramètres pour le trapeze:")
                result_lines.extend(parametres_trapeze)
            elif "line" in line:
                # Extract arguments: coordinates x1, y1, x2, y2, and RGB color
                coordonnees_raw = raw_args[2].strip("\"")   # Coordinates in the form "x1, y1, x2, y2"
                coordonnees = tuple(map(int, map(str.strip, coordonnees_raw.split(",")))) # Convert to a tuple (x1, y1, x2, y2)
                r, g, b = couleur  # Couleur RGB
                x1, y1, x2, y2 = coordonnees  # Extract coordinates x1, y1, x2, y2
                if not code_to_insert.check_comment_in_code(global_functions, "void drawLine"):
                    global_functions.append("// Définition de la fonction drawLine")
                    global_functions.extend(code_to_insert.code_drawLine)
                parametres_line = code_to_insert.get_parametres_line(x1, y1, x2, y2, r, g, b)
                result_lines.append("// Paramètres pour le line:")
                result_lines.extend(parametres_line)
    elif line.startswith("window"):
        arguments = line[line.find("(") + 1: line.rfind(")")]
        coordonnees, x, y, r, g, b = code_to_insert.extract_window_params(arguments)
        parametres_window = code_to_insert.get_parametres_window(x, y, r, g, b)
        result_lines.append("// Paramètres pour la fenêtre avec dimensions personnalisées :")
        result_lines.extend(parametres_window)
        if not code_to_insert.check_comment_in_code(result_lines, "//Create window custom"):
            result_lines.append("//Create window custom")
            result_lines.extend(code_to_insert.code_create_window_modify)
        window_created[0] = True
        result_lines.append("    window_created = true;")
    elif line.startswith("call "):
        match_call = re.match(r'^call\s+([a-zA-Z_]\w*)\s*\((.*)\)$', line)
        if match_call:
            function_name = match_call.group(1)
            args = match_call.group(2).strip()
            if args == "":
                result_lines.append(f"{function_name}(renderer);")
            else:
                result_lines.append(f"{function_name}(renderer, {args});")
        else:
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
 
         # Check if the value is an expression
        if re.search(r'[+\-*/]', value):
            terms = re.split(r'([+\-*/])', value)
            for term in terms:
                term = term.strip()
                if re.match(r'[a-zA-Z_]\w*', term) and term not in {'+', '-', '*', '/'}:
                    if term not in symbol_table:
                        raise ValueError(f"Variable '{term}' not declared.")
                     # Verify the type of the variable used
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
            # Assume the value is another variable
            if value not in symbol_table:
                raise ValueError(f"Variable '{value}' not declared.")
            var_type = symbol_table[value]["type"]
            result_lines.append(f"{var_type} {var_name} = {value};")
 
        # Update the symbol_table with the new variable
        symbol_table[var_name] = {"type": var_type}
 
 
    elif line.startswith("print"):
        line = re.sub(r'print\((.+?)\)',
                      lambda m: translate_print(m, symbol_table),
                      line)
        result_lines.append(line + ";")
 
    else:
        # By default, keep the line as-is
        result_lines.append(line)
 
    return result_lines
 
 
