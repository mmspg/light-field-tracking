import tkinter as tk
from PIL import ImageTk, Image

BG_COLOR = "grey"
IMG_PATH_PREFIX = "img/"


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self._geom = '1000x800+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom


root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)
root.title("lf-tracking")
root.configure(background=BG_COLOR)


def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))


class ImageMatrix:
    def __init__(self, width, height, imgX, imgY, unit):
        self.width = width
        self.height = height
        self.baseImgX = imgX
        self.baseImgY = imgY
        self.curImgX = imgX
        self.curImgY = imgY
        self.unit = unit
        self.clickX = 0
        self.clickY = 0
        self.initPanels()

    def initPanels(self):
        self.panel1 = tk.Label(root)
        self.panel1.pack(side="left", fill="both", expand="yes")
        self.panel2 = tk.Label(root)
        self.panel2.pack(side="right", fill="both", expand="yes")

        self.panel1.bind('<Button-1>', self.click)
        self.panel1.bind('<B1-Motion>', self.move)
        self.panel2.bind('<Button-1>', self.click)
        self.panel2.bind('<B1-Motion>', self.move)
        self.updateImages()

    def click(self, event):
        self.clickX, self.clickY = (event.x, event.y)
        self.baseImgX = self.curImgX
        self.baseImgY = self.curImgY
        return

    def move(self, event):
        diffX = self.clickX - event.x
        diffY = self.clickY - event.y

        imgDiffX = int(round(diffX / float(self.unit)))
        imgDiffY = int(round(diffY / float(self.unit)))

        newImgX = clamp(self.baseImgX + imgDiffX, 0, self.width - 1)
        newImgY = clamp(self.baseImgY + imgDiffY, 0, self.height - 1)
        if (newImgX != self.curImgX or newImgY != self.curImgY):
            self.curImgX = newImgX
            self.curImgY = newImgY
            self.updateImages()

    def updateImages(self):
        imgPath = IMG_PATH_PREFIX + '{}_{}.jpg'.format(self.curImgX, self.curImgY)

        newImg = ImageTk.PhotoImage(Image.open(imgPath))
        self.panel1.configure(image=newImg)
        self.panel1.image = newImg
        self.panel2.configure(image=newImg)
        self.panel2.image = newImg


imgMatrix = ImageMatrix(3, 3, 1, 1, 100)


app = FullScreenApp(root)
root.mainloop()
