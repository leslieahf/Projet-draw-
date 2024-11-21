# Function to translate Draw++ to C
def translate_to_c(draw_code):
    # Replace Draw++ syntax with C syntax
    draw_code = draw_code.replace(" <- ", " = ")  # Draw++ assignment
    draw_code = draw_code.replace(" eq ", " == ")  # Draw++ equality check
    draw_code = draw_code.replace(" neq ", " != ")  # Draw++ inequality check
    draw_code = draw_code.replace("&", "&&")  # Draw++ AND
    draw_code = draw_code.replace(" OR ", " || ")  # Draw++ OR
    draw_code = draw_code.replace("function", "function")  # Draw++ function
    draw_code = draw_code.replace(" if", "if")  # if statement
    draw_code = draw_code.replace(" else", "else")  # else statement
    
    # No semicolon after function call or declaration
    lines = draw_code.split("\n")
    for i, line in enumerate(lines):
        if line.strip().endswith(";"):
            lines[i] = line.strip()[:-1]  # Remove semicolon from lines
    
    return "\n".join(lines)
