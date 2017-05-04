import tkinter as tk
from PIL import ImageTk, Image
import datetime

BG_COLOR = "darkgrey"
IMG_PATH_PREFIX = "img/"

f_tracking = open('tracking.txt', 'w')
f_answers = open('answers.txt', 'w')


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
    """Clamps the value x between a minimum and a maximum."""

    assert (minimum <= maximum)
    return max(minimum, min(maximum, x))


class Point:
    "Represents a 2D point"

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
    """"Represents a light-field image."""

    def __init__(self, img_name, nb_img_x, nb_img_y, nb_img_z, base_img=None, focus_depth=None, unit=20):
        """Initializes a light-field image.
        
        :param img_name: The name of the image (i.e. of the folder containing all its image files).
        :param nb_img_x: The number of images in the x-axis.
        :param nb_img_y: The number of images in the y-axis.
        :param nb_img_z: The number of images in the z-axis (i.e. depth)
        :param base_img: The Point representing the first image to display. If it is None, the middle center image is taken.
        :param focus_depth: The initial depth that should be in focus.
        :param unit: The number of pixels one should move the mouse to switch to the next image.
        """

        self.img_name = img_name
        self.nb_img_x = nb_img_x
        self.nb_img_y = nb_img_y
        self.nb_img_z = nb_img_z

        if base_img is None:
            self.base_img = Point(nb_img_x // 2, nb_img_y // 2)
        else:
            self.base_img = base_img

        self.last_img = self.base_img
        self.cur_img = self.base_img
        self.next_img = self.base_img
        self.focus_depth = focus_depth
        self.unit = unit
        self.img_onscreen = [[datetime.timedelta(0) for x in range(nb_img_y)] for y in range(nb_img_x)]
        self.click_pos = Point(0, 0)
        self.prev_time = 0
        self.cur_time = 0
        self.panels = None

    def click(self, click_pos):
        """Stores the mouse position and the image diplayed at the time of the click.
        
        This method should be called whenever an image is clicked on.
        
        :param click_pos: The position of the mouse when clicking.
        """
        self.click_pos = click_pos
        self.base_img = self.cur_img

    def move(self, move_pos):
        """Change the image displayed w.r.t. the mouse position.

        This method should be called when the mouse is dragged over an image.

        :param move_pos: The current position of the mouse.
        """
        diff_x = self.click_pos.x - move_pos.x
        diff_y = self.click_pos.y - move_pos.y

        img_diff_x = int(round(diff_x / float(self.unit)))
        img_diff_y = int(round(diff_y / float(self.unit)))

        self.next_img = Point(clamp(self.base_img.x + img_diff_x, 0, self.nb_img_x - 1),
                              clamp(self.base_img.y + img_diff_y, 0, self.nb_img_y - 1))

        if self.next_img != self.cur_img:
            self.update_images()

    def refocus(self, new_focus):
        """Displays the image corresponding to the given focus depth.
        
        :param new_focus: The depth to focus to image on.
        """
        self.next_img = Point(self.nb_img_x // 2, self.nb_img_y // 2)
        self.focus_depth = int(new_focus)
        self.update_images()

    def update_images(self):
        """Updates the image displayed according to the current attributes of the LFImage."""

        self.close_img()

        self.last_img = self.cur_img
        self.cur_img = self.next_img

        if self.focus_depth is None:
            img_name = '{}/{:03}_{:03}.png'.format(self.img_name, self.cur_img.x, self.cur_img.y)
        else:
            img_name = '{}/{:03}_{:03}_{:03}.png'.format(self.img_name, self.cur_img.x, self.cur_img.y, self.focus_depth)

        new_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + img_name))

        self.panels[0].configure(image=new_img)
        self.panels[0].image = new_img
        self.panels[1].configure(image=new_img)
        self.panels[1].image = new_img

        f_tracking.write("Displaying '{}'  start: {}  ".format(img_name, self.cur_time.strftime('%H:%M:%S.%f')))

    def close_img(self):
        """Perform actions necessary when and image is replaced by another.
        
        This method is used to write the end time and on-screen time in the tracking.txt file.
        """
        self.prev_time = self.cur_time
        self.cur_time = datetime.datetime.now()

        if self.prev_time != 0:
            onscreen = self.cur_time - self.prev_time
            self.img_onscreen[self.cur_img.x][self.cur_img.y] += onscreen
            total_onscreen = self.img_onscreen[self.cur_img.x][self.cur_img.y]

            f_tracking.write("end: {}  on-screen: {}  total on-screen: {}\n".format(self.cur_time.strftime('%H:%M:%S.%f'),
                                                                                  onscreen,
                                                                                  total_onscreen))

    def set_panels(self, panels):
        """Configure the LFImage to use the given panels for display.
        
        :param panels: 
        """
        self.panels = panels


class TestSession:
    """Represents a test session for the assessment of images."""

    def __init__(self, images, question, possible_answers, answers_description):
        """Initializes a test session.
        
        :param images: The light-field images to use for the test session.
        :param question: The question that should be asked.
        :param answers_description: A short text describing the possible answers to the question.
        :param answers: The possible answers to the question.
        """
        self.images = images
        self.question = question
        self.possible_answers = possible_answers
        self.answers_description = answers_description
        self.panels = None
        self.focus_scale = None
        self.is_focus_enabled = False
        self.img_index = 0
        self.img_index_label = None
        self.message_label = None
        self.cur_img = images[self.img_index]
        self.answers = [None] * len(images)
        self.ended = False

        self.setup_gui()

        for img in self.images:
            img.set_panels(self.panels)

        self.cur_img.update_images()
        self.display_img_index()

    def setup_gui(self):
        """Sets up the graphical user interface needed for the test session"""

        # Main frame containing all GUI objects
        main_frame = tk.Frame(background=BG_COLOR)

        self.img_index_label = tk.Label(main_frame, background=BG_COLOR, pady=10)
        self.img_index_label.grid(row=0, column=0, columnspan=3)

        tk.Label(main_frame, text="Test", background=BG_COLOR).grid(row=1, column=0, pady=5)
        tk.Label(main_frame, text="Reference", background=BG_COLOR).grid(row=1, column=2)

        # Panels where the two images are displayed
        self.panels = [tk.Label(main_frame, background=BG_COLOR), tk.Label(main_frame, background=BG_COLOR)]
        self.panels[0].grid(row=2, column=0)
        self.panels[1].grid(row=2, column=2)

        self.panels[0].bind('<Button-1>', self.click)
        self.panels[0].bind('<B1-Motion>', self.move)
        self.panels[1].bind('<Button-1>', self.click)
        self.panels[1].bind('<B1-Motion>', self.move)

        # Scale (slider) to allow refocusing
        focus_frame = tk.Frame(main_frame, background=BG_COLOR, padx=5)
        self.focus_scale = tk.Scale(focus_frame, from_=self.cur_img.nb_img_z-1, to=0, command= self.refocus,
                                    showvalue=0, length=200, background=BG_COLOR)
        self.focus_scale.grid(row=1, column=0)
        tk.Label(focus_frame, text="Far", background=BG_COLOR).grid(row=0, column=0)
        tk.Label(focus_frame, text="Near", background=BG_COLOR).grid(row=2, column=0)
        focus_frame.grid(row=2, column=1)

        question_label = tk.Label(main_frame, text=self.question, background=BG_COLOR, pady=30)
        question_label.grid(row=3, column=0, columnspan=3)

        # Frame containing all the buttons representing the possible answers
        buttons_frame = tk.Frame(main_frame, background=BG_COLOR)

        for i in range(len(self.possible_answers)):
            answer = self.possible_answers[i]
            btn_width = 12
            btn = tk.Button(buttons_frame, text=str(answer), command=lambda a=answer: self.answer(a),
                            width=btn_width, highlightbackground=BG_COLOR)
            btn.grid(row=0, column=(i), padx = 12)
            tk.Label(buttons_frame, text=self.answers_description[i], width=btn_width, wraplength=btn_width*10, background=BG_COLOR).grid(row=1, column=(i))

            # We can answer with the keys 1-9 if the number of answers is smaller than 10
            if len(self.possible_answers) <= 9:
                root.bind(str(i + 1), lambda e, a=self.possible_answers[i]: self.answer(a))

        buttons_frame.grid(row=5, column=0, columnspan=3)

        main_frame.place(anchor="c", relx=.50, rely=.50)

        root.protocol("WM_DELETE_WINDOW", self.close)

    def next_img(self, event):
        """Displays the next image"""

        if not self.is_last_image():
            self.cur_img.close_img()
            self.cur_img.cur_time = 0
            f_tracking.write("<next>\n")
            self.img_index += 1
            self.cur_img = self.images[self.img_index]
            self.focus_scale.configure(from_=self.cur_img.nb_img_z-1)
            if self.cur_img.focus_depth is not None:
                self.focus_scale.set(self.cur_img.focus_depth)
            self.cur_img.update_images()
            self.display_img_index()

    def answer(self, answ):
        """Stores the answer given by the user.
        
        :param answ: The answer.
        """
        self.answers[self.img_index] = answ
        f_answers.write("{:30} : {}\n".format(self.cur_img.img_name, answ))

        if self.is_last_image() and not self.ended:
            self.ended = True
            end_msg = tk.Label(root, text="FINISHED", background=BG_COLOR)
            end_msg.pack(fill="both", expand="true")
        else:
            self.next_img(None)

    def click(self, event):
        """Method  called whenever an image is clicked on."""

        click_pos = Point(event.x, event.y)
        self.cur_img.click(click_pos)
        return

    def move(self, event):
        """Method  called when the mouse is dragged over an image."""

        self.reset_focus()

        move_pos = Point(event.x, event.y)
        self.cur_img.move(move_pos)
        return

    def refocus(self, new_focus):
        if self.is_focus_enabled:
            self.cur_img.refocus(new_focus)
        else:
            self.is_focus_enabled = True

    def reset_focus(self):
        self.is_focus_enabled = False
        self.focus_scale.set(0)
        self.cur_img.focus_depth = None
        self.cur_img.update_images()

    def display_img_index(self):
        """Displays the index of the current image in a text label."""

        self.img_index_label.configure(text="Image {}/{}".format(self.img_index + 1, len(self.images)))

    def is_last_image(self):
        """Return True iff the current image displayed is the last one."""

        return self.img_index >= (len(self.images) - 1)

    def close(self):
        """Method called when the window is closed"""

        self.cur_img.close_img()

        f_tracking.flush()
        f_tracking.close()
        f_answers.flush()
        f_answers.close()

        root.quit()


###############
## MAIN CODE ##
###############

root = tk.Tk()
root.title("lf-tracking")
root.configure(background=BG_COLOR)

images = [None] * 6
images[0] = LFImage("Bikes",                 15, 15, 11)
images[1] = LFImage("Danger_de_Mort",        15, 15, 11)
images[2] = LFImage("Flowers",               15, 15, 11)
images[3] = LFImage("Fountain_&_Vincent_2",  15, 15, 11)
images[4] = LFImage("Friends_1",             15, 15, 11)
images[5] = LFImage("Stone_Pillars_Outside", 15, 15, 11)

question = "How would you rate the impairment of the test image (left) compared to the reference image (right)?"
answers = [1, 2, 3, 4, 5]
answers_description = ["Very annoying",
                       "Annoying",
                       "Slightly annoying",
                       "Perceptible, but not annoying",
                       "Imperceptible"]

TestSession(images, question, answers, answers_description)

app = FullScreenApp(root)
root.mainloop()
