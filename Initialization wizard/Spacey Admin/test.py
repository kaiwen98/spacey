import tkinter as tk
import random

def draw_square(event):
    x0 = random.randint(30, 370)
    y0 = random.randint(30, 170)
    size = random.randint(10, 30)

    event.widget.create_rectangle(x0, y0, x0+size, y0+size, fill="red")

def give_focus(event):
    event.widget.focus_set()
    event.widget.configure(background="bisque")

def lose_focus(event):
    event.widget.configure(background="white")

root = tk.Tk()
label = tk.Label(root, text="Click to focus a canvas, press 's' to draw a square")
canvas1 = tk.Canvas(root, width=400, height=200, background="white",
                    borderwidth=1, relief="raised")
canvas2 = tk.Canvas(root, width=400, height=200, background="white",
                    borderwidth=1, relief="raised")

label.pack(side="top", fill="x")
canvas1.pack(fill="both", expand=True)
canvas2.pack(fill="both", expand=True)

for canvas in (canvas1, canvas2):
    canvas.bind("<FocusOut>",lose_focus)
    canvas.bind("<1>", give_focus)
    canvas.bind("<s>", draw_square)

root.mainloop()