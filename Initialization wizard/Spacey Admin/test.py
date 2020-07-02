"""
import tkinter as tk
import tkSimpleDialog


root = tk.Tk()

root.state('zoomed') # Full window view
root.title('Title') # Set title name
root.configure(bg = "gray22") #Bg colour
tkSimpleDialog.askstring("fuck you", "please" , initialvalue = "fuck", parent = root)

root.mainloop()
"""
from tkinter import *


root = Tk()
root.lift()
w = 300; h = 200; x = 10; y = 10
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

Label(root, text = "Menu Choices:").grid(row=1, column =0)
Label(root, text='1. Baloney and cheese').grid(row=2, column=0, pady=4)
Label(root, text='2. Roast chicken and gravy').grid(row=3, column=0, pady=4)
Label(root, text='3. Pear salad').grid(row=4, column=0, pady=4)
Label(root, text='4. Cateloupe and brocoli soup').grid(row=5, column=0, pady=4)

def store_entry():
  print ("Entry stored as " + str(ent.get()))

def exit_entry():
  print("Entry cancelled")
  top.destroy()

top = Toplevel()
top.title('Franks Restaurant')
top.geometry("%dx%d+%d+%d" % (w, h, w+x+20, y))
Label(top, text='Please choose your meal').place(x=10,y=10)
ent = Entry(top); 
ent.place(x=10, y=50); 
ent.focus()
Button(top, text="OK", command=store_entry).place(x=10, y=150) 
Button(top, text="Cancel", command=exit_entry).place(x=60, y=150)  

root.mainloop()
