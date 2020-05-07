from core import applyToFile
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class InverseGenerator(Tk):
    def __init__(self):
        super().__init__()
        self.title("HowToPlayLN's 4k Inverse Generator")
        self.browse = ttk.LabelFrame(self, width=128, height=72)
        self.browse.grid(column=1, row=1)
        self.run = ttk.LabelFrame(self, width=128, height=72)
        self.run.grid(column=1, row=2)
        self.openfile()
    
    def fileDialog(self):
        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("osu files","*.osu"),("all files","*.*")))
        self.label = ttk.Label(self.browse, text = "")
        self.label.grid(column = 1, row = 1)
        self.label.configure(text = self.filename)
        self.showbookmarks()
    
    def openfile(self):
        self.openfile_button = ttk.Button(self.browse, text="Open File", command=self.fileDialog)
        self.openfile_button.grid(column=1, row=2)
    
    def showbookmarks(self):
        self.bookmarks_button = ttk.Button(self.browse, text="Show all bookmarks", command=self.analyzebookmarks)
        self.bookmarks_button.grid(column=1, row=3)
    
    def analyzebookmarks(self):
        self.file = applyToFile(self.label['text'])
        bookmarks = self.file.bookmarks
        self.bookmarklabel = []
        for start, end in bookmarks:
            self.bookmarklabel.append(ttk.Label(self.run, text="Start: {}, End: {}, LN gap: 1/".format(start, end)))
        self.entries = [ttk.Entry(self.run) for k in self.bookmarklabel]
        i = 1
        for a, b in zip(self.bookmarklabel, self.entries):
            a.grid(row = i, column=1)
            b.grid(row=i, column=2)
            i += 1
        self.idx = i
        self.InverseButton()
        
    def DoInverse(self):
        gap = [int(i.get()) if i.get() != "" else 4 for i in self.entries]
        self.file.inverse(gap)
        self.file.writefile("Inverse")
        for k in self.run.winfo_children():
            k.destroy()
    
    def InverseButton(self):
        self.Inverse_Button = ttk.Button(self.run, text="Inverse !", command=self.DoInverse)
        self.Inverse_Button.grid(row=self.idx, column=1)

if __name__ == "__main__":
    k = InverseGenerator()
    k.mainloop()