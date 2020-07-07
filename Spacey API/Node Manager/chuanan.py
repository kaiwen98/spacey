from tkinter import *

root = Tk()
root.state('zoomed')
root.title("lol")
root.configure(bg = "red")
print(root.winfo_screenheight())
print(root.winfo_screenwidth())
root.mainloop()