import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

# Main window
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

# Run Python code
def run_code():
    code = text_area.get("1.0", tk.END)
    with open("temp_code.py", "w") as file:
        file.write(code)
    result = subprocess.run(["python3", "temp_code.py"], capture_output=True, text=True)
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, result.stdout + result.stderr)

# Clear editor
def clear_editor():
    if messagebox.askyesno("Reset", "Clear all content?"):
        text_area.delete("1.0", tk.END)

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
file_menu.add_command(label="Reset", command=clear_editor)
file_menu.add_separator()
file_menu.add_command(label="Quit", command=on_close)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Toolbar
toolbar_frame = tk.Frame(root, bg="#282a36")
toolbar_frame.pack(fill=tk.X)

# Run button
run_button = tk.Button(toolbar_frame, text="Run Python", command=run_code, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
run_button.pack(side=tk.LEFT, padx=5, pady=5)

# Reset button
reset_button = tk.Button(toolbar_frame, text="Reset Editor", command=clear_editor, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
reset_button.pack(side=tk.LEFT, padx=5, pady=5)

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

# Function to generate C code
def generate_c_code():
    code = text_area.get("1.0", tk.END)  # Get the text from the editor
    if "afficher une liste" in code.lower():  # Check if the text contains "afficher une liste"
        c_code = """
#include <stdio.h>

int main() {
    int list[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    
    // Print the elements of the list
    for (int i = 0; i < 10; i++) {
        printf("%d\\n", list[i]);
    }

    return 0;
}
"""
        with open("generated_list_display.c", "w") as file:
            file.write(c_code)
        
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Code C generated: generated_list_display.c\n")
        print("Code C generated in 'generated_list_display.c'.")

# Add Generate C button to toolbar
generate_button = tk.Button(toolbar_frame, text="Generate C Code", command=generate_c_code, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
generate_button.pack(side=tk.LEFT, padx=5, pady=5)

# Function to compile and run the C code
def compile_and_run_c_code():
    # Compile the generated C file
    compile_command = ["gcc", "generated_list_display.c", "-o", "generated_list_display"]
    result = subprocess.run(compile_command, capture_output=True, text=True)
    
    # If compilation is successful
    if result.returncode == 0:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Compilation successful, running C program...\n")
        
        # Run the compiled program
        run_command = ["./generated_list_display"]
        execution_result = subprocess.run(run_command, capture_output=True, text=True)
        
        # Display the output of the execution
        output_area.insert(tk.END, "Execution result:\n")
        output_area.insert(tk.END, execution_result.stdout)
    else:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Compilation error:\n")
        output_area.insert(tk.END, result.stderr)

# Add Run C button to toolbar
run_c_button = tk.Button(toolbar_frame, text="Run C Code", command=compile_and_run_c_code, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
run_c_button.pack(side=tk.LEFT, padx=5, pady=5)

# Main loop
root.mainloop()
