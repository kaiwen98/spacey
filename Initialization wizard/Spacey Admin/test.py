from tkinter import *
from tkinter import ttk
from tkinter import filedialog
 
 
 
class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Python Tkinter Dialog Widget")
        self.minsize(640, 400)
        #self.wm_iconbitmap('icon.ico')
 
        self.labelFrame = ttk.LabelFrame(self, text = "Open File")
        help(ttk.LabelFrame)
        self.labelFrame.grid(row = 0, padx = 20, pady = 20)
 
        self.button()
 
 
 
    def button(self):
        self.button = ttk.Button(self.labelFrame, text = "Browse A File",command = self.fileDialog)
        self.button.grid(row = 1)
 
 
    def fileDialog(self):
 
        filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("jpeg files","*.jpg"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(row = 2)
        self.label.configure(text = filename)
 
 
 
 
 
root = Root()
root.mainloop()