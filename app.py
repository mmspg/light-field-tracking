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
    def __init__(self, img_name, width, height, base_img, panels, unit=20):
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

        img_name = '{}/{:03}_{:03}.png'.format(self.img_name, self.cur_img.x, self.cur_img.y)
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

def rate(rating):
    print(rating)

root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)
root.title("lf-tracking")

main_frame = tk.Frame()

panel1 = tk.Label(main_frame)
panel1.grid(row=0, column=0)
panel2 = tk.Label(main_frame)
panel2.grid(row=0, column=1)

panel1.configure(text="Test")
panel2.configure(text="Reference")
panels = [panel1, panel2]

buttons_frame = tk.Frame(pady=20)

for i in range(1, 6):
    btn = tk.Button(buttons_frame, text=str(i), command = rate(i), width=6, highlightbackground=BG_COLOR)
    btn.grid(row=0, column=(i-1))
    btn.configure(background=BG_COLOR)

buttons_frame.grid(in_=main_frame, row=1, column=0, columnspan=2)


main_frame.place(anchor="c", relx=.50, rely=.50)

images = [None] * 6
images[0] = LFImage("Bikes", 15, 15, Point(7, 7), panels)
images[1] = LFImage("Danger_de_Mort", 15, 15, Point(7, 7), panels)
images[2] = LFImage("Flowers", 15, 15, Point(7, 7), panels)
images[3] = LFImage("Fountain_&_Vincent_2", 15, 15, Point(7, 7), panels)
images[4] = LFImage("Friends_1", 15, 15, Point(7, 7), panels)
images[5] = LFImage("Stone_Pillars_Outside", 15, 15, Point(7, 7), panels)

slideshow = Slideshow(images, panels)

root.bind('<Left>', slideshow.prev_img)
root.bind('<Right>', slideshow.next_img)

root.protocol("WM_DELETE_WINDOW", slideshow.close)

panel1.configure(background=BG_COLOR)
panel2.configure(background=BG_COLOR)
buttons_frame.configure(background=BG_COLOR)
main_frame.configure(background=BG_COLOR)
root.configure(background=BG_COLOR)

app = FullScreenApp(root)
root.mainloop()
