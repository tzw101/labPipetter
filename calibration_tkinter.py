#GUI for calibration
import Tkinter
from PIL import Image, ImageTk

class Calibration(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.geometry("250x380")
        self.grid()
        self.canvas = Tkinter.Canvas(self)
        self.canvas.grid(sticky=Tkinter.N+Tkinter.E+Tkinter.S+Tkinter.W)

        self.width = 120
        self.height = 150

        image_file = Image.open(r"C:\Users\user\Desktop\arrow.png")
        self.PIL_image = ImageTk.PhotoImage(image_file.convert("RGBA"))
        self.canvas.create_image(self.width,self.height,image=self.PIL_image)
        self.canvas.bind("<Button-1>", self.callback)

        button = Tkinter.Button(self,text=u"Click me !", command=self.OnButtonClick)
        button.grid(sticky = 'W')

        self.labelVariable = Tkinter.StringVar()
        label = Tkinter.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1)
        self.labelVariable.set(u"1x")

    def callback(self,event):
        width = self.width
        height = self.height
        if width-9 < event.x < width+9 and height-24 < event.y < height-12:
            print "clicked up arrow!"
        elif width-9 < event.x < width+9 and height+12 < event.y < height+24:
            print "clicked down arrow!"
        elif width+12 < event.x < width+25 and height-8 < event.y < height+8:
            print "clicked right arrow!"
        elif width-25 < event.x < width-12 and height-8 < event.y < height+8:
            print "clicked left arrow!"

    def OnButtonClick(self):
        if self.labelVariable.get() == '1x':
            self.labelVariable.set('10x')
        elif self.labelVariable.get() == '10x':
            self.labelVariable.set('1x')

if __name__ == '__main__':

    test = Calibration(None)
    test.title('Test')
    test.mainloop()