import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import syntaxe
from tok import Lexer
from parseur import Parser
import translate_to_c
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

root = tk.Tk()
root.title("IDE DRAW++")

# Open file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, file.read())

# Save file
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_area.get("1.0", tk.END))

# Line numbers
def update_line_numbers():
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete("1.0", tk.END)
    lines = text_area.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines)):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state=tk.DISABLED)
    line_numbers.after(100, update_line_numbers)

# Confirm to quit
def on_close():
    if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Menu
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=on_close)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Editor frame
editor_frame = tk.Frame(root, bg="#282a36")
editor_frame.pack(fill=tk.BOTH, expand=True)

# Line numbers
line_numbers = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0, background="#44475a", fg="#f8f8f2", state=tk.DISABLED)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# Text area
text_area = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, width=80, height=20, bg="#282a36", fg="#f8f8f2", insertbackground="#f8f8f2", relief=tk.FLAT)
text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Output area
output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10, bg="#282a36", fg="#f8f8f2", insertbackground="#f8f8f2", relief=tk.FLAT)
output_area.pack(fill=tk.BOTH, expand=True)

# Update line numbers every 100 ms
update_line_numbers()

# Highlight error
def highlight_error(line_number, column_start, column_end):
    text_area.tag_remove("error", "1.0", tk.END)  # Supprime les anciens soulignages
    start_index = f"{line_number}.{column_start}"
    end_index = f"{line_number}.{column_end}"
    text_area.tag_add("error", start_index, end_index)  # Ajoute le soulignage rouge
    text_area.tag_config("error", underline=1, foreground="#E57373")  # Configure le style

# Generate and run C code
def generate_and_run_c_code():
    draw_code = text_area.get("1.0", tk.END).strip()  # Récupère le code de l'éditeur

    # Vérification si l'utilisateur a tapé "help()"
    if draw_code.lower() == "help()":
        display_help()  # Affiche les instructions
        return

    # Validation complète via syntaxe.py
    errors, tokens, ast = syntaxe.validate_code(draw_code)
    if errors:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Erreurs détectées :\n")
        for error in errors:
            output_area.insert(tk.END, f"{error}\n")
            if "line" in error:
                try:
                    line_number = int(error.split("line")[1].split()[0])
                    column_start = 0
                    column_end = len(draw_code.split("\n")[line_number - 1])
                    highlight_error(line_number, column_start, column_end)
                except (ValueError, IndexError):
                    pass
        output_area.insert(tk.END, "\n\nExécution annulée.")
        return

    # Si tout est OK, continuez avec la traduction en C et l'exécution
    try:
        c_code = translate_to_c.translate_to_c(draw_code)
        with open("generated_program.c", "w") as file:
            file.write(c_code)

        compile_command = ["gcc", "generated_program.c", "-o", "generated_program", "-lSDL2", "-lSDL2_ttf", "-lm"]
        result = subprocess.run(compile_command, capture_output=True, text=True)

        if result.returncode == 0:
            output_area.delete("1.0", tk.END)
            output_area.insert(tk.END, "Compilation réussie, exécution du programme...\n")
            run_command = ["./generated_program"]
            execution_result = subprocess.run(run_command, capture_output=True, text=True)
            output_area.insert(tk.END, "Résultat de l'exécution :\n")
            output_area.insert(tk.END, execution_result.stdout)
        else:
            output_area.delete("1.0", tk.END)
            output_area.insert(tk.END, "Erreur de compilation :\n")
            output_area.insert(tk.END, result.stderr)

    except Exception as e:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, f"Erreur lors de la traduction ou exécution : {str(e)}\n\nExécution annulée.")

# Add Generate and Run button
run_button = tk.Button(root, text="Run draw code", command=generate_and_run_c_code, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
run_button.pack(fill=tk.X, padx=5, pady=5)

# Function to display help instructions
def display_help(event=None):
    help_text = """
    DRAW++ COMMANDS:
    ------------------
    1. draw commands :
        draw(cercle,"R,G,B","x,y",rayon)
        draw(rectangle,"R,G,B","x,y",largeur,hauteur)
        draw(triangle,"R,G,B","x1,y1,x2,y2,x3,y3")
        draw(line,"R,G,B","x1,y1,x2,y2")
        drax(losange,"R,G,B","x,y",largeur,hauteur)
        draw(carre,"R,G,B","x,y",cote)
        draw(polygon,"R,G,B","x,y",rayon,n)
        draw(trapeze,"R,G,B","x,y",base1,base2,hauteur)
    2. boucles:
        variable <- valeur
        for(variable;varable condition valeur;variable++){
        //bloc instruction
        }
    3. condition:
        if(variable condition valeur){
        bloc instruction
        }else{
        //bloc instruction
        }
    4. fonction:
        func nomfonction(variable){
        //bloc instruction
        return 0;
        }
        call nomfonction()

    Type these commands in the editor and execute them!
    """
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, help_text)

text_area.bind("<Return>", lambda event: check_help_command())

# Function to check for "help()" command
def check_help_command():
    current_text = text_area.get("1.0", tk.END).strip()
    if current_text.endswith("help()"):
        display_help()

# Main loop
root.mainloop()

 
