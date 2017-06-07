import tkinter as tk
from PIL import Image, ImageTk

from helper import BG_COLOR, NB_IMAGES_PRELOADED, IMG_PATH_PREFIX, f_tracking, f_answers, Helper


class TestSession:
    """Represents a test session for the assessment of light field images.

    This class controls which LF image is displayed, handles user input by transmitting it
    to the current LF image if necessary, and writes the grades given to the output file, among other things.
    """

    def __init__(self, images, question, possible_answers, answers_description,
                 show_preview, preload_images, assessment_method, test_image_side=None):
        """Initializes a test session.

        :param images: The light-field images to use for the test session.
        :param question: The question that should be asked.
        :param possible_answers: The possible answers to the question.
        :param answers_description: The descriptions corresponding to each of the answers in possible_answers.
        :param show_preview: if True, show the preview animation for each image
        :param preload_images: if True, preloads the images for a smoother experience (recommended)
        :param assessment_method: Assessment method to be used in the test session.
                                  It should be either Helper.IQA.SINGLE_STIMULUS or Helper.IQA.SINGLE_STIMULUS
        :param test_image_side: Side on which the test image should be displayed.
                                This should be either Helper.Side.LEFT or Helper.Side.Right
        """

        self.images = images
        self.question = question
        self.possible_answers = possible_answers
        self.answers_description = answers_description
        self.show_preview = show_preview
        self.preload_images = preload_images
        self.assessment_method = assessment_method
        self.test_image_side = test_image_side
        self.panels = None
        self.img_index = 0
        self.img_index_label = None
        self.message_label = None
        self.cur_img = images[self.img_index]
        self.answers = [None] * len(images)

        self.root = tk.Tk()
        self.root.title("lf-tracking")
        self.root.configure(background=BG_COLOR)
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))

        self.logo_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + "mmspg.png"))

        if self.preload_images:
            # Loads the first few images asynchronously
            for i in range(NB_IMAGES_PRELOADED + 1):
                print("Loading image {}/{}...".format(i + 1, len(self.images)))
                self.images[i].load_images(self.assessment_method)

        if show_preview:
            self.start_btn = tk.Button(self.root, text="START", command=self.start_session,
                                       highlightbackground=BG_COLOR)
            self.start_btn.pack(expand=True, anchor="center")

            self.logo_start = tk.Label(self.root, background=BG_COLOR)
            self.logo_start.configure(image=self.logo_img)
            self.logo_start.pack(side="bottom")

        else:
            self.start_session()

        self.root.mainloop()

    def start_session(self):
        """Starts the test session"""

        self.setup_gui()

        for img in self.images:
            img.set_panels(self.panels)
            img.set_test_image_side(self.test_image_side)

        if self.preload_images and not self.cur_img.is_loaded:
            Helper.fullscreen_msg.config(text="Loading image...")
            Helper.fullscreen_msg.pack(fill="both", expand="true")

        # Start by either showing the preview or the normal interactive view
        if self.show_preview:
            self.start_btn.destroy()
            self.logo_start.destroy()
            self.cur_img.preview()
        else:
            self.cur_img.update_images()

    def setup_gui(self):
        """Sets up the graphical user interface needed for the test session"""

        # Main frame containing all GUI objects
        main_frame = tk.Frame(background=BG_COLOR)

        self.img_index_label = tk.Label(main_frame, background=BG_COLOR, pady=10)
        self.img_index_label.grid(row=0, column=0, columnspan=3)

        # Display "Test" and "Reference" labels
        test_label = tk.Label(main_frame, background=BG_COLOR)
        ref_label = tk.Label(main_frame, background=BG_COLOR)
        if self.assessment_method is Helper.IQA.DOUBLE_STIMULUS:
            test_label.configure(text="Test")
            ref_label.configure(text="Reference")

        test_col = 2 * self.test_image_side.value
        ref_col = 2 - test_col
        test_label.grid(row=1, column=test_col, pady=5)
        ref_label.grid(row=1, column=ref_col, pady=5)

        # Panel(s) where the image(s) is(are) displayed
        if self.assessment_method is Helper.IQA.DOUBLE_STIMULUS:
            self.panels = [tk.Label(main_frame, background=BG_COLOR), tk.Label(main_frame, background=BG_COLOR)]
            self.panels[0].grid(row=2, column=0)
            self.panels[1].grid(row=2, column=2)
        elif self.assessment_method is Helper.IQA.SINGLE_STIMULUS:
            self.panels = [tk.Label(main_frame, background=BG_COLOR)]
            self.panels[0].grid(row=2, column=0)


        for panel in self.panels:
            panel.bind('<Button-1>', self.click)
            panel.bind('<B1-Motion>', self.move)
            panel.bind('<Double-Button-1>', self.refocus_to_point)

        # Scale (a.k.a. slider) to perform refocusing
        focus_frame = tk.Frame(main_frame, background=BG_COLOR, padx=5)
        self.focus_slider = tk.Scale(focus_frame, from_=self.cur_img.nb_img_depth - 1, to=0,
                                     command=self.slider_refocus_to_depth,
                                     showvalue=0, length=200, background=BG_COLOR)
        self.focus_slider.grid(row=1, column=0)
        tk.Label(focus_frame, text="Far", background=BG_COLOR).grid(row=0, column=0)
        tk.Label(focus_frame, text="Near", background=BG_COLOR).grid(row=2, column=0)
        focus_frame.grid(row=2, column=1)
        Helper.is_focus_slider_enabled = False
        Helper.focus_slider = self.focus_slider

        question_label = tk.Label(main_frame, text=self.question, background=BG_COLOR, pady=30)
        question_label.grid(row=3, column=0, columnspan=3)

        # Frame containing all the buttons representing the possible answers
        buttons_frame = tk.Frame(main_frame, background=BG_COLOR)

        for i in range(len(self.possible_answers)):
            answer = self.possible_answers[i]
            btn_width = 12
            btn = tk.Button(buttons_frame, text=str(answer), command=lambda a=answer: self.answer(a),
                            width=btn_width, highlightbackground=BG_COLOR)
            btn.grid(row=0, column=i, padx=12)
            tk.Label(buttons_frame, text=self.answers_description[i], width=btn_width, wraplength=btn_width * 10,
                     background=BG_COLOR).grid(row=1, column=i)

            # We can answer with the keys 1-9 if the number of answers is smaller than 10
            if len(self.possible_answers) <= 9:
                self.root.bind(str(i + 1), lambda e, a=self.possible_answers[i]: self.answer(a))

        buttons_frame.grid(row=5, column=0, columnspan=3)

        main_frame.place(anchor="c", relx=.50, rely=.50)

        self.display_img_index()

        # Information message used when loading inmage and when the test session ends
        Helper.fullscreen_msg = tk.Label(self.root, text="", background=BG_COLOR)
        Helper.fullscreen_msg.pack_forget()

        # MMSPG Logo
        logo_label = tk.Label(self.root, background=BG_COLOR)
        logo_label.configure(image=self.logo_img)
        logo_label.pack(side="bottom", anchor="e")

    def next_img(self):
        """Displays the next image"""

        if not self.is_last_image():
            self.cur_img.close_img()
            self.cur_img.clear_memory()
            self.cur_img.cur_time = 0
            self.img_index += 1
            self.cur_img = self.images[self.img_index]

            if self.preload_images:
                # Display loading message is image is not loaded yet
                if not self.cur_img.is_loaded:
                    Helper.fullscreen_msg.config(text="Loading image...")
                    Helper.fullscreen_msg.pack(fill="both", expand="true")

                # Preload the following image already
                if self.img_index + NB_IMAGES_PRELOADED < len(self.images):
                    print("Loading image {}/{}...".format(self.img_index + NB_IMAGES_PRELOADED + 1, len(self.images)))
                    self.images[self.img_index + NB_IMAGES_PRELOADED].load_images(self.assessment_method)

            self.display_img_index()
            f_tracking.write("\n")

            # Reset slider value to 0
            Helper.is_focus_slider_enabled = False
            Helper.focus_slider.set(0)

            if self.show_preview:
                self.cur_img.preview()
            else:
                self.cur_img.update_images()

    def answer(self, answ):
        """Stores the answer given by the user.
        
        :param answ: The answer.
        """
        self.answers[self.img_index] = answ
        f_answers.write("{:30}: {}\n".format(self.cur_img.img_name, answ))

        if self.is_last_image():
            self.finish_test_session()
        else:
            self.next_img()

    def click(self, event):
        """Method  called whenever an image is clicked on."""

        self.cur_img.click((event.x, event.y))
        return

    def move(self, event):
        """Method  called when the mouse is dragged over an image."""

        self.cur_img.move((event.x, event.y))
        return

    def slider_refocus_to_depth(self, focus_depth):
        """Displays the image corresponding to the given focus depth.
        
        :param focus_depth: The depth to focus to image on.
        """
        if Helper.is_focus_slider_enabled:
            self.cur_img.refocus_to_depth(focus_depth)
        else:
            Helper.is_focus_slider_enabled = True

    def refocus_to_point(self, event):
        """Refocus the current image on the given point using the depth map

        :param event: The event that triggered the refocusing and contains the point coordinates
        """
        self.cur_img.refocus_to_point(event)

    def display_img_index(self):
        """Displays the index of the current image in a text label."""

        self.img_index_label.configure(text="Image {}/{}".format(self.img_index + 1, len(self.images)))

    def is_last_image(self):
        """Return True iff the current image displayed is the last one."""

        return self.img_index >= (len(self.images) - 1)

    def finish_test_session(self):
        """Called at the end of the test session to close all files and display a message"""

        self.cur_img.close_img()
        self.cur_img.clear_memory()

        f_tracking.flush()
        f_tracking.close()
        f_answers.flush()
        f_answers.close()

        Helper.fullscreen_msg.config(text="Thank you!")
        Helper.fullscreen_msg.pack(fill="both", expand="true")
