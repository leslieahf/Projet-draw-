import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import translate_to_c
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
 
# Function to generate and execute C code
def generate_and_run_c_code():
    # Translate DRAW++ code to C
    draw_code = text_area.get("1.0", tk.END)  # Get the text from the editor
    c_code = translate_to_c.translate_to_c(draw_code)
    
    # Save the translated C code into a file
    with open("generated_program.c", "w") as file:
        file.write(c_code)
    
    # Compile the generated C file
    compile_command = ["gcc", "generated_program.c", "-o", "generated_program", "-lSDL2" ,"-lm"]
    result = subprocess.run(compile_command, capture_output=True, text=True)
    
    # Check for compilation errors
    if result.returncode == 0:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Compilation successful, running C program...\n")
        
        # Run the compiled program
        run_command = ["./generated_program"]
        execution_result = subprocess.run(run_command, capture_output=True, text=True)
        
        # Display the output of the execution
        output_area.insert(tk.END, "Execution result:\n")
        output_area.insert(tk.END, execution_result.stdout)
    else:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Compilation error:\n")
        output_area.insert(tk.END, result.stderr)
 
# Add Generate and Run button
run_button = tk.Button(root, text="Run draw code", command=generate_and_run_c_code, bg="#44475a", fg="#f8f8f2", relief=tk.FLAT)
run_button.pack(fill=tk.X, padx=5, pady=5)
 
# Function to display help instructions
def display_help(event=None):
    help_text = """
    DRAW++ COMMANDS:
    ------------------
    1. draw_line(x1, y1, x2, y2): Draws a line from (x1, y1) to (x2, y2).
    2. draw_circle(x, y, radius): Draws a circle with center (x, y) and given radius.
    3. draw_rectangle(x, y, width, height): Draws a rectangle with top-left (x, y).
    4. set_color(r, g, b): Sets the color for future drawing commands.
    5. clear(): Clears the drawing canvas.
 
    Type these commands in the editor and execute them!
    """
    output_area.delete("1.0", tk.END)
    output_area.insert(tk.END, help_text)
 
# Bind 'help' command detection to the editor
text_area.bind("<Return>", lambda event: check_help_command())
 
def check_help_command():
    current_text = text_area.get("1.0", tk.END).strip()
    if current_text.endswith("help"):
        display_help()
 
# Main loop
root.mainloop()
 
 
