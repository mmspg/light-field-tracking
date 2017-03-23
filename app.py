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


def clamp(x, minimum, maximum):
    assert (minimum <= maximum)
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


class LFImage:
    def __init__(self, img_name, width, height, base_img, panels, unit=60):
        self.img_name = img_name
        self.width = width
        self.height = height
        self.base_img = base_img
        self.last_img = base_img
        self.cur_img = base_img
        self.next_img = base_img
        self.panels = panels
        self.unit = unit
        self.img_duration = [[datetime.timedelta(0) for x in range(height)] for y in range(width)]
        self.click_pos = Point(0, 0)
        self.prev_time = 0
        self.cur_time = 0


    def click(self, click_pos):
        self.click_pos = click_pos
        self.base_img = self.cur_img
        return

    def move(self, move_pos):
        diff_x = self.click_pos.x - move_pos.x
        diff_y = self.click_pos.y - move_pos.y

        img_diff_x = int(round(diff_x / float(self.unit)))
        img_diff_y = int(round(diff_y / float(self.unit)))

        self.next_img = Point(clamp(self.base_img.x + img_diff_x, 0, self.width - 1),
                        clamp(self.base_img.y + img_diff_y, 0, self.height - 1))

        if self.next_img != self.cur_img:
            self.update_images()

    def update_images(self):
        self.close_img()

        self.last_img = self.cur_img
        self.cur_img = self.next_img

        img_name = '{}_{:02}_{:02}.jpg'.format(self.img_name, self.cur_img.x, self.cur_img.y)
        new_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + img_name))

        self.panels[0].configure(image=new_img)
        self.panels[0].image = new_img
        self.panels[1].configure(image=new_img)
        self.panels[1].image = new_img


        f.write("Displaying '{}'  start: {}  ".format(img_name, self.cur_time.strftime('%H:%M:%S.%f')))

    def close_img(self):
        self.prev_time = self.cur_time
        self.cur_time = datetime.datetime.now()

        if self.prev_time != 0:
            duration = self.cur_time - self.prev_time
            self.img_duration[self.cur_img.x][self.cur_img.y] += duration
            total_duration = self.img_duration[self.cur_img.x][self.cur_img.y]

            f.write("end: {}  duration: {}  total duration: {}\n".format(self.cur_time.strftime('%H:%M:%S.%f'),
                                                                         duration,
                                                                         total_duration))


class Slideshow:
    def __init__(self, images, panels, base_img_index=0):
        self.images = images
        self.img_index = base_img_index
        self.cur_img = images[base_img_index]
        self.cur_img.update_images()

        self.panels = panels

        self.panels[0].bind('<Button-1>', self.click)
        self.panels[0].bind('<B1-Motion>', self.move)
        self.panels[1].bind('<Button-1>', self.click)
        self.panels[1].bind('<B1-Motion>', self.move)


    def next_img(self, event):
        if (self.img_index + 1)  <= (len(self.images)-1):
            self.cur_img.close_img()
            self.cur_img.cur_time = 0
            f.write("<next>\n")
            self.img_index += 1
            self.cur_img = self.images[self.img_index]
            self.cur_img.update_images()

    def prev_img(self, event):
        if (self.img_index - 1)  >= 0:
            self.cur_img.close_img()
            self.cur_img.cur_time = 0
            f.write("<previous>\n")
            self.img_index -= 1
            self.cur_img = self.images[self.img_index]
            self.cur_img.update_images()

    def click(self, event):
        click_pos = Point(event.x, event.y)
        self.cur_img.click(click_pos)
        return

    def move(self, event):
        move_pos = Point(event.x, event.y)
        self.cur_img.move(move_pos)
        return

    def close(self):
        self.cur_img.close_img()

        f.flush()
        f.close()
        root.quit()


root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)
root.title("lf-tracking")
root.configure(background=BG_COLOR)

panel1 = tk.Label(root)
panel1.pack(side="left", fill="both", expand="yes")
panel2 = tk.Label(root)
panel2.pack(side="right", fill="both", expand="yes")
panels = [panel1, panel2]

img0 = LFImage("img0", 3, 3, Point(1, 1), panels)
img1 = LFImage("img1", 3, 3, Point(1, 1), panels)
img2 = LFImage("img2", 3, 3, Point(1, 1), panels)

slideshow = Slideshow([img0, img1, img2], panels)

root.bind('<Left>', slideshow.prev_img)
root.bind('<Right>', slideshow.next_img)

root.protocol("WM_DELETE_WINDOW", slideshow.close)

app = FullScreenApp(root)
root.mainloop()
