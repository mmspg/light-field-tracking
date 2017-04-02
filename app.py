import tkinter as tk
from PIL import ImageTk, Image
import datetime

BG_COLOR = "grey"
IMG_PATH_PREFIX = "img/"

f_tracking = open('tracking.txt', 'w')
f_ratings = open('ratings.txt', 'w')


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
    def __init__(self, img_name, width, height, base_img=None, focus_point=0, unit=20):
        self.img_name = img_name
        self.width = width
        self.height = height

        if base_img is None:
            self.base_img = Point(width//2, height//2)
        else:
            self.base_img = base_img

        self.last_img = self.base_img
        self.cur_img = self.base_img
        self.next_img = self.base_img
        self.focus_point = focus_point
        self.unit = unit
        self.img_duration = [[datetime.timedelta(0) for x in range(height)] for y in range(width)]
        self.click_pos = Point(0, 0)
        self.prev_time = 0
        self.cur_time = 0
        self.panels = None


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

    def refocus(self, new_focus):
        self.focus_point = new_focus
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

        f_tracking.write("Displaying '{}'  start: {}  ".format(img_name, self.cur_time.strftime('%H:%M:%S.%f')))

    def close_img(self):
        self.prev_time = self.cur_time
        self.cur_time = datetime.datetime.now()

        if self.prev_time != 0:
            duration = self.cur_time - self.prev_time
            self.img_duration[self.cur_img.x][self.cur_img.y] += duration
            total_duration = self.img_duration[self.cur_img.x][self.cur_img.y]

            f_tracking.write("end: {}  duration: {}  total duration: {}\n".format(self.cur_time.strftime('%H:%M:%S.%f'),
                                                                         duration,
                                                                         total_duration))

    def set_panels(self, panels):
        self.panels = panels


class TestSession:
    def __init__(self, images, questions, answers_scale, answers):
        self.images = images
        self.questions = questions
        self.answers_scale = answers_scale
        self.answers = answers
        self.panels = None
        self.focus_scale = None
        self.img_index = 0
        self.img_index_label = None
        self.message_label = None
        self.cur_img = images[self.img_index]
        self.ratings = [None] * len(images)
        self.ended = False

        self.setup_gui()

        for img in self.images:
            img.set_panels(self.panels)
            
        self.cur_img.update_images()
        self.display_img_index()

    def setup_gui(self):
        main_frame = tk.Frame(background=BG_COLOR)

        tk.Label(main_frame, text="Test", background=BG_COLOR).grid(row=0, column=0)
        tk.Label(main_frame, text="Reference", background=BG_COLOR).grid(row=0, column=2)

        self.panels = [tk.Label(main_frame, background=BG_COLOR), tk.Label(main_frame, background=BG_COLOR)]
        self.panels[0].grid(row=1, column=0)
        self.panels[1].grid(row=1, column=2)

        self.panels[0].bind('<Button-1>', self.click)
        self.panels[0].bind('<B1-Motion>', self.move)
        self.panels[1].bind('<Button-1>', self.click)
        self.panels[1].bind('<B1-Motion>', self.move)

        focus_frame = tk.Frame(main_frame, background=BG_COLOR, padx=5)
        self.focus_scale = tk.Scale(focus_frame, from_=10, to=0, command=self.cur_img.refocus, showvalue=0, length=200, background=BG_COLOR)
        self.focus_scale.grid(row=1, column=0)
        tk.Label(focus_frame, text="Far", background=BG_COLOR).grid(row=0, column=0)
        tk.Label(focus_frame, text="Near", background=BG_COLOR).grid(row=2, column=0)
        focus_frame.grid(row=1, column=1)

        self.img_index_label = tk.Label(main_frame, background=BG_COLOR, pady=10)
        self.img_index_label.grid(row=2, column=0, columnspan=3)

        question_label = tk.Label(main_frame, text=question, background=BG_COLOR)
        question_label.grid(row=3, column=0, columnspan=3)

        answers_scale_label = tk.Label(main_frame, text=answers_scale, justify="left", background=BG_COLOR)
        answers_scale_label.grid(row=4, column=0, columnspan=3)

        buttons_frame = tk.Frame(main_frame, background=BG_COLOR)

        for i in range(len(answers)):
            btn = tk.Button(buttons_frame, text=str(answers[i]), command=lambda a=answers[i]: self.rate(a), width=6,
                            highlightbackground=BG_COLOR)
            btn.grid(row=0, column=(i))

            if len(answers) <= 9:
                root.bind(str(i+1), lambda e, a=answers[i]: self.rate(a))

        buttons_frame.grid(row=5, column=0, columnspan=3, pady=10)

        main_frame.place(anchor="c", relx=.50, rely=.50)

        root.protocol("WM_DELETE_WINDOW", self.close)

    def next_img(self, event):
        if (self.img_index + 1)  <= (len(self.images)-1):
            self.cur_img.close_img()
            self.cur_img.cur_time = 0
            f_tracking.write("<next>\n")
            self.img_index += 1
            self.cur_img = self.images[self.img_index]
            self.cur_img.update_images()
            self.display_img_index()

    def rate(self, rating):
        self.ratings[self.img_index] = rating
        f_ratings.write("{:30} : {}\n".format(self.cur_img.img_name, rating))

        if self.is_rating_complete() and not self.ended:
            self.ended = True
            end_msg = tk.Label(root, text="FINISHED", background=BG_COLOR)
            end_msg.pack(fill="both", expand="true")
        else:
            self.next_img(None)

    def click(self, event):
        click_pos = Point(event.x, event.y)
        self.cur_img.click(click_pos)
        return

    def move(self, event):
        move_pos = Point(event.x, event.y)
        self.cur_img.move(move_pos)
        return

    def display_img_index(self):
        self.img_index_label.configure(text="Image {}/{}".format(self.img_index+1, len(self.images)))

    def is_rating_complete(self):
        ret = True
        for r in self.ratings:
            if r is None: ret = False

        return ret

    def close(self):
        self.cur_img.close_img()

        f_tracking.flush()
        f_tracking.close()
        f_ratings.flush()
        f_ratings.close()

        root.quit()


root = tk.Tk()
root.title("lf-tracking")
root.configure(background=BG_COLOR)

images = [None] * 6
images[0] = LFImage("Bikes", 15, 15)
images[1] = LFImage("Danger_de_Mort", 15, 15)
images[2] = LFImage("Flowers", 15, 15)
images[3] = LFImage("Fountain_&_Vincent_2", 15, 15)
images[4] = LFImage("Friends_1", 15, 15)
images[5] = LFImage("Stone_Pillars_Outside", 15, 15)

question = "How would you rate the impairment of the test image (left) compared to the reference image (right)?"
answers_scale = "1 : very annoying\n" \
                "2 : annoying\n" \
                "3 : slightly annoying\n" \
                "4 : perceptible, but not annoying\n" \
                "5 : imperceptible\n"
answers = [1, 2, 3, 4, 5]

TestSession(images, question, answers_scale, answers)


app = FullScreenApp(root)
root.mainloop()
