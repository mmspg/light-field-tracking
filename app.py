import tkinter as tk
from PIL import ImageTk, Image
import datetime

BG_COLOR = "grey"
IMG_PATH_PREFIX = "img/"
IMG_NAMES = ["img0", "img1", "img2"]

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


class ImageMatrix:
    def __init__(self, width, height, base_img, unit, img_index=0):
        self.width = width
        self.height = height
        self.base_img = base_img
        self.last_img = base_img
        self.cur_img = base_img
        self.unit = unit
        self.img_index = img_index
        self.img_duration = [[datetime.timedelta(0) for x in range(height)] for y in range(width)]
        self.click_pos = Point(0, 0)
        self.prev_time = 0
        self.cur_time = 0
        self.init_panels()

    def init_panels(self):
        self.panel1 = tk.Label(root)
        self.panel1.pack(side="left", fill="both", expand="yes")
        self.panel2 = tk.Label(root)
        self.panel2.pack(side="right", fill="both", expand="yes")

        self.panel1.bind('<Button-1>', self.click)
        self.panel1.bind('<B1-Motion>', self.move)
        self.panel2.bind('<Button-1>', self.click)
        self.panel2.bind('<B1-Motion>', self.move)
        self.update_images()

    def click(self, event):
        self.click_pos = Point(event.x, event.y)
        self.base_img = self.cur_img
        return

    def move(self, event):
        diff_x = self.click_pos.x - event.x
        diff_y = self.click_pos.y - event.y

        img_diff_x = int(round(diff_x / float(self.unit)))
        img_diff_y = int(round(diff_y / float(self.unit)))

        new_img = Point(clamp(self.base_img.x + img_diff_x, 0, self.width - 1),
                        clamp(self.base_img.y + img_diff_y, 0, self.height - 1))

        if new_img != self.cur_img:
            self.last_img = self.cur_img
            self.cur_img = new_img
            self.update_images()

    def next_img(self, event):
        if (self.img_index + 1)  <= (len(IMG_NAMES)-1):
            self.img_index += 1
            self.update_images()

    def prev_img(self, event):
        if (self.img_index - 1)  >= 0:
            self.img_index -= 1
            self.update_images()

    def update_images(self):
        img_name = '{}_{:02}_{:02}.jpg'.format(IMG_NAMES[self.img_index], self.cur_img.x, self.cur_img.y)

        new_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + img_name))
        self.panel1.configure(image=new_img)
        self.panel1.image = new_img
        self.panel2.configure(image=new_img)
        self.panel2.image = new_img

        self.write_end_duration()

        f.write("Displaying '{}'  start: {}  ".format(img_name, self.cur_time.strftime('%H:%M:%S.%f')))

    def write_end_duration(self):
        self.prev_time = self.cur_time
        self.cur_time = datetime.datetime.now()

        if self.prev_time != 0:
            duration = self.cur_time - self.prev_time
            self.img_duration[self.last_img.y][self.last_img.x] += duration
            total_duration = self.img_duration[self.last_img.y][self.last_img.x]

            f.write("end: {}  duration: {}  total duration: {}\n".format(self.cur_time.strftime('%H:%M:%S.%f'),
                                                                         duration,
                                                                         total_duration))

    def close(self):
        self.write_end_duration()

        f.flush()
        f.close()
        root.quit()


img_matrix = ImageMatrix(3, 3, Point(1, 1), 60)
root.focus_set()
root.bind('<Left>', img_matrix.prev_img)
root.bind('<Right>', img_matrix.next_img)

root.protocol("WM_DELETE_WINDOW", img_matrix.close)

app = FullScreenApp(root)
root.mainloop()
