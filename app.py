import tkinter as tk
from PIL import ImageTk, Image

BG_COLOR = "grey"
IMG_PATH_PREFIX = "img/"

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='1000x800+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)
root.title("lf-tracking")
root.configure(background=BG_COLOR)

img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX+"4.jpg"))
panel1 = tk.Label(root, image = img)
panel1.pack(side = "left", fill = "both", expand = "yes")
panel2 = tk.Label(root, image = img)
panel2.pack(side = "right", fill = "both", expand = "yes")

def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))

class ImageMatrix:
    def __init__(self, width, height, imgX, ImgY, unit):
        self.width = width
        self.height = height
        self.baseImgX = imgX
        self.baseImgY = ImgY
        self.curImgX = imgX
        self.curImgY = ImgY
        self.unit = unit
        self.updateImages()

    def move(self, diffX, diffY):
        imgDiffX = int(round(diffX/float(self.unit)))
        imgDiffY = int(round(diffY/float(self.unit)))

        newImgX = clamp(self.baseImgX + imgDiffX, 0, self.width-1)
        newImgY = clamp(self.baseImgY + imgDiffY, 0, self.height-1)
        if (newImgX != self.curImgX or newImgY != self.curImgY):
            self.curImgX = newImgX
            self.curImgY = newImgY
            self.updateImages()

    def updateImages(self):
        imgId = self.curImgY*self.width + self.curImgX
        imgPath = IMG_PATH_PREFIX + str(imgId) + ".jpg"

        neImg = ImageTk.PhotoImage(Image.open(imgPath))
        panel1.configure(image=neImg)
        panel1.image = neImg
        panel2.configure(image=neImg)
        panel2.image = neImg

    def release(self, event):
        self.baseImgX = self.curImgX
        self.baseImgY = self.curImgY


imgMatrix = ImageMatrix(3, 3, 1, 1, 100)

class Mouse:
    def __init__(self):
        self.clickX = 0
        self.clickY = 0

    def click(self, event):
        self.clickX, self.clickY =  (event.x, event.y)
        return

    def move(self, event):
        imgMatrix.move(self.clickX-event.x, self.clickY-event.y)
        return


mouse = Mouse()
panel1.bind('<Button-1>',mouse.click)
panel1.bind('<B1-Motion>',mouse.move)
panel1.bind('<ButtonRelease-1>',imgMatrix.release)
panel2.bind('<Button-1>',mouse.click)
panel2.bind('<B1-Motion>',mouse.move)
panel2.bind('<ButtonRelease-1>',imgMatrix.release)

app=FullScreenApp(root)
root.mainloop()