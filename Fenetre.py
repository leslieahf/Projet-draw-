import tkinter as tk

# Fonction de mise à jour du curseur
def update_cursor(event):
    canvas.delete("cursor")
    x, y = event.x, event.y
    # Dessine le curseur sous forme de petite croix
    cursor_size = 5
    canvas.create_line(x - cursor_size, y, x + cursor_size, y, fill="blue", tags="cursor")
    canvas.create_line(x, y - cursor_size, x, y + cursor_size, fill="black", tags="cursor")

def draw(event):
    x, y = event.x, event.y
    canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="black", outline="black")

#Création de la fenêtre
root = tk.Tk()
root.title("Dessin avec curseur")

# Création d'un canvas qui servira de toile afin de dessiner
canvas = tk.Canvas(root, width=500, height=500, bg="white")
canvas.pack()

# ReLier le mouvement de la souris à la mise à jour du curseur
canvas.bind("<Motion>", update_cursor)
# ReLier le clic gauche de la souris pour dessiner
canvas.bind("<B1-Motion>", draw)

#Faire un boucle indéfinit pour ne pas arrêter l'affichage
root.mainloop()
