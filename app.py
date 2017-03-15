import tkinter as tk
from PIL import ImageTk, Image
import datetime

BG_COLOR = "grey"
IMG_PATH_PREFIX = "img/"
f = open('output.txt', 'w')


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

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class ImageMatrix:
    def __init__(self, width, height, baseImg, unit):
        self.width = width
        self.height = height
        self.baseImg = baseImg
        self.prevImg = baseImg
        self.curImg = baseImg
        self.imgDuration = [[datetime.timedelta(0) for x in range(height)] for y in range(width)]
        self.unit = unit
        self.clickPos = Point(0,0)
        self.prevTime = 0
        self.curTime = 0
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
        self.clickPos = Point(event.x, event.y)
        self.baseImg = self.curImg
        return

    def move(self, event):
        diffX = self.clickPos.x - event.x
        diffY = self.clickPos.y - event.y

        imgDiffX = int(round(diffX / float(self.unit)))
        imgDiffY = int(round(diffY / float(self.unit)))

        newImgX = clamp(self.baseImg.x + imgDiffX, 0, self.width - 1)
        newImgY = clamp(self.baseImg.y + imgDiffY, 0, self.height - 1)
        newImg = Point(newImgX, newImgY)

        if (newImg != self.curImg):
            self.prevImg = self.curImg
            self.curImg = newImg
            self.updateImages()

    def updateImages(self):
        imgName = '{}_{}.jpg'.format(self.curImg.x, self.curImg.y)

        newImg = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + imgName))
        self.panel1.configure(image=newImg)
        self.panel1.image = newImg
        self.panel2.configure(image=newImg)
        self.panel2.image = newImg

        self.writeEndDuration()

        f.write("Displaying '{}'  start: {}  ".format(imgName, self.curTime.strftime('%H:%M:%S.%f')))

    def writeEndDuration(self):
        self.prevTime = self.curTime
        self.curTime = datetime.datetime.now()

        if (self.prevTime != 0):
            duration = self.curTime - self.prevTime
            self.imgDuration[self.prevImg.y][self.prevImg.x] += duration
            totalDuration = self.imgDuration[self.prevImg.y][self.prevImg.x]

            f.write("end: {}  duration: {}  total duration: {}\n".format(self.curTime.strftime('%H:%M:%S.%f'), duration,
                                                                         totalDuration))

    def close(self):
        self.writeEndDuration()

        f.flush()
        f.close()
        root.quit()


imgMatrix = ImageMatrix(3, 3, Point(1, 1), 60)

root.protocol("WM_DELETE_WINDOW", imgMatrix.close)

app = FullScreenApp(root)
root.mainloop()
