from tkinter import *

def command(event):
    print(E1.get())
    E1.delete(0,100)

top = Tk()
top.minsize(640, 400)
L1 = LabelFrame(top, text="User Name")
L1.grid(row = 0, column = 0)
E1 = Entry(L1, bd =5, command = print("haha"))
E1.grid(row = 1, column = 0, pady = 10)
E1.bind("<Return>", command)

top.mainloop()