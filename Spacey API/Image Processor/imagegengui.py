from tkinter import *
import tkinter as tk
from tkinter import filedialog
from imagegen import imagegen
import p_config as cfg
from functools import partial
from tkinter import font

class menu_upload(object):
    def __init__(self, frame):
        self.frame = frame
        self.labelFrame = LabelFrame(self.frame, text = "Floor Plan Manager",  bg = "gray55")
        self.labelFrame.pack(fill = X, side = TOP, pady = 10, padx = 10)
        self.obj = Button(self.labelFrame, text = "Generate Occupancy Graphic", command = self.fileupload)
        self.obj.pack(ipadx = 10, ipady = 10, fill = X, side = TOP)
        self.label = Label(self.labelFrame, text = "", bg = "gray55", bd = 2)
        self.label.pack(fill = X, padx = 2, pady = 2)
        self.label.configure(text = "Press <Ctrl-Z for help!>", bg = "sky blue")
        self.label.update()
 
    def fileupload(self):
        self.label.configure(text = "Generating image...", bg = "yellow")
        self.label.update()
        try:
            cfg.json_path = filedialog.askopenfilename(initialdir = cfg.json_folder, title = "Select File", filetypes = [("Json file","*.json*")])
            imagegen()
            self.label.configure(text = "Done! Awaiting next upload.", bg = "pale green")
            self.label.update()
        
        except:
            self.label.configure(text = "Failed... Error with JSON file. Try again", bg = "IndianRed1")
            self.label.update()
            

def findCentralize(root):
    width = root.winfo_reqwidth()/2
    height = root.winfo_reqheight()/2

    return int(root.winfo_screenwidth()/2 - width), int(root.winfo_screenheight()/2 - height)

def displayHelpMenu(event, root):
    helpMenu = Toplevel(root)
    helpMenu.geometry('300x300')
    helpMenu.title("Help Menu")
    helpMenu.iconbitmap(cfg.icon_path)
    x,y = findCentralize(helpMenu)
    helpMenu.geometry("+{}+{}".format(x, y))
    frame = Frame(helpMenu, bg = "gray10")
    frame.pack(fill = "both", padx = 5, pady = 5)
    help = helpMessage(frame)
    helpMenu.configure(bg = "sky blue")
    helpMenu.bind('<Escape>', lambda event: quitTop(event, helpMenu))


def helpMessage(frame):
    cfg.help_font = font.Font(family="Arial", size=8, weight = "bold")
    text = Text(frame,  bg = "white", font = cfg.help_font, bd = 5, wrap = WORD)
    yscroll = Scrollbar(frame, orient = "vertical", command = text.yview)
    yscroll.pack(padx = 2, pady = 2, side = LEFT, fill = Y)
    text.pack(pady = 2, ipadx = 2, ipady = 2, side = LEFT, fill = Y)
    text.configure(yscrollcommand = yscroll.set)

    text.tag_config("h1", foreground = "deepskyblue2")
    text.tag_config("h2", foreground = "black")
    text.insert(END, "Info:", "h1")
    text.insert(END, "\n    This Image Processor GUI Menu allows you to upload a JSON file generated from Spacey Node Manager,"+ 
                     "and generate respective occupancy graphic that corresponds to the floor plan that was worked on in the respective session. "+
                     "\n  Upon initializing, the Image Processor will generate a map with the nodes drawn in the respective coordinate position as outlined in the JSON file. Thereafter, the color of each drawn node will be updated depending on the occupancy status of the corresponding seat as monitored by the sensor node on-site.", "h2")
    text.insert(END, "\n\nControls:", "h1")
    text.insert(END, "\n>> Interact with button for file upload.", "h2")
    text.insert(END, "\n>> The images are saved in /spacey/images/output graphic", "h2")
    text.insert(END, "\n\nDisclaimer:", "h1")
    text.insert(END, "\n    This Image Processor is only a demonstration of the backend image transformation capabilities, but it is unlikely to be part "+ 
                     "of the workflow during actual operation. \n   The backend service will be active to generate the PNG image upon user query or upon update in seat status, and does not require the GUI shell to function.", "h2")
    text.configure(state = "disabled")


def quitTop(event, top):
    top.destroy()
    top.update()

def destroy(event, root):
    root.destroy()

def main():
    _root = tk.Tk()
    _root.geometry('300x110')
    x,y = findCentralize(_root)
    _root.geometry("+{}+{}".format(x, y))
    _root.title("Image generator")
    _root.configure(bg = "gray22")
    upload = menu_upload(_root)
    _root.iconbitmap(cfg.icon_path)
    _root.bind('<Escape>', lambda event: destroy(event, _root))
    _root.bind('<Control-z>', lambda event: displayHelpMenu(event, _root))

    _root.mainloop()





