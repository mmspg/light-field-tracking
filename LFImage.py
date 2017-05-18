import datetime
from threading import Timer

from PIL import Image, ImageTk

from SubapertureImage import SubapertureImage
from helper import IMG_PATH_PREFIX, IMG_FORMAT, clamp, f_tracking


class LFImage:
    """"Represents a light-field image."""

    def __init__(self, img_name, nb_img_x, nb_img_y, nb_img_depth, test_img_padding, base_img=None, focus_depth=None, unit=20):
        """Initializes a light-field image.
        
        :param img_name: The name of the image (i.e. of the folder containing all its image files).
        :param nb_img_x: The number of images in the x-axis.
        :param nb_img_y: The number of images in the y-axis.
        :param nb_img_depth: The number of depth images (i.e. z-axis)
        :param base_img: The Point representing the first image to display. 
                         If it is None, the middle center image is taken.
        :param focus_depth: The initial depth that should be in focus.
        :param unit: The number of pixels one should move the mouse to switch to the next image.
        """

        self.img_name = img_name
        self.reference_img_name = img_name.split("R")[0]+"R0"
        self.nb_img_x = nb_img_x
        self.nb_img_y = nb_img_y
        self.nb_img_depth = nb_img_depth
        self.test_img_padding = test_img_padding

        if base_img is None:
            # Take the center perspective image
            self.base_img = SubapertureImage(nb_img_x // 2, nb_img_y // 2, focus_depth)
        else:
            self.base_img = base_img

        self.unit = unit

        self.test_images = [[None for i in range(nb_img_x)] for j in range(nb_img_y)]
        self.ref_images = [[None for i in range(nb_img_x)] for j in range(nb_img_y)]

        self.cur_img = None
        self.next_img = self.base_img
        self.depth_map = Image.open("{}/depth_map/{}.{}".format(IMG_PATH_PREFIX, self.reference_img_name, IMG_FORMAT)).load()
        self.img_onscreen = [[datetime.timedelta(0) for x in range(nb_img_y)] for y in range(nb_img_x)]
        self.click_pos = (0, 0)
        self.prev_time = 0
        self.cur_time = 0
        self.panels = None
        self.test_image_side = None

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
        diff_x = self.click_pos[0] - move_pos[0]
        diff_y = self.click_pos[1] - move_pos[1]

        img_diff_x = int(round(diff_x / float(self.unit)))
        img_diff_y = int(round(diff_y / float(self.unit)))

        self.next_img = SubapertureImage(clamp(self.base_img.x + img_diff_x, 0, self.nb_img_x - 1),
                                         clamp(self.base_img.y + img_diff_y, 0, self.nb_img_y - 1),
                                         None)

        self.update_images()

    def refocus_to_depth(self, focus_depth):
        """Displays the image corresponding to the given focus depth.
        
        :param focus_depth: The depth to focus to image on.
        """
        self.next_img = SubapertureImage(self.nb_img_x // 2, self.nb_img_y // 2, int(focus_depth))
        self.update_images()

    def refocus_to_point(self, event):
        """Refocus the current image on the given point using the depth map

        :param event: The event that triggered the refocusing and contains the point coordinates
        """
        depth_map_value = self.depth_map[event.x, event.y] / 255
        focus_depth = round(depth_map_value * (self.nb_img_depth-1))
        self.refocus_animation(focus_depth)

    def refocus_animation(self, depth):
        """Animates the refocusing to the given depth in a smooth transition
        
        :param depth: The final depth at the end of the animation
        """
        if self.cur_img.focus_depth is not None:
            if self.cur_img.focus_depth != depth:
                depthDelta = 1 if (depth - self.cur_img.focus_depth > 0) else -1
                new_depth = self.cur_img.focus_depth + depthDelta
                self.refocus_to_depth(new_depth)

                if(new_depth != depth):
                    Timer(0.01, lambda: self.refocus_animation(depth)).start()
        else:
            self.refocus_to_depth(depth)


    def update_images(self):
        """Updates the image displayed according to the next_img attribute"""

        if self.next_img != self.cur_img:
            self.close_img()

            self.cur_img = self.next_img

            if self.cur_img.focus_depth is None:
                # Display a normal image
                test_img_name = '{}/{:03}_{:03}.{}'.format(self.img_name, self.cur_img.x, self.cur_img.y, IMG_FORMAT)
                ref_img_name = '{}/{:03}_{:03}.{}'.format(self.reference_img_name, self.cur_img.x, self.cur_img.y, IMG_FORMAT)

                new_test_img = self.test_images[self.cur_img.x][self.cur_img.y]
                new_ref_img = self.ref_images[self.cur_img.x][self.cur_img.y]

            else:
                # Display a refocused image
                test_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.img_name, self.cur_img.x, self.cur_img.y,
                                                            self.cur_img.focus_depth, IMG_FORMAT)
                ref_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.reference_img_name, self.cur_img.x, self.cur_img.y,
                                                            self.cur_img.focus_depth, IMG_FORMAT)

            # Load the images if they were not already loaded
            if new_test_img is None:
                new_test_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + test_img_name))
                self.test_images[self.cur_img.x][self.cur_img.y] = new_test_img
            if new_ref_img is None:
                new_ref_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + ref_img_name))
                self.ref_images[self.cur_img.x][self.cur_img.y] = new_ref_img

            # Set the test and reference image on the correct side (left=0, right=1)
            self.panels[self.test_image_side.value].configure(image=new_test_img)
            self.panels[self.test_image_side.value].image = new_test_img
            self.panels[(self.test_image_side.value + 1) % 2].configure(image=new_ref_img)
            self.panels[(self.test_image_side.value + 1) % 2].image = new_ref_img

            f_tracking.write("{}  start: {}  ".format(test_img_name, self.cur_time.strftime('%H:%M:%S.%f')))

    def load_images(self):
        print("load_images")
        for x in range(self.nb_img_x):
            for y in range(self.nb_img_y):
                test_img_name = '{}/{:03}_{:03}.{}'.format(self.img_name, x, y, IMG_FORMAT)
                ref_img_name = '{}/{:03}_{:03}.{}'.format(self.reference_img_name, x, y, IMG_FORMAT)
                self.ref_images[x][y] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + ref_img_name))

                pad = self.test_img_padding
                if(pad <= x and x < self.nb_img_x - pad and
                   pad <= y and y < self.nb_img_y - pad):
                    self.test_images[x][y] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + test_img_name))

    def preview(self):
        """Display a preview of the image by going through a predefined subset of the sub-aperture images."""

        def preview_inner(index):
            img_name = '{}/007_{:03}.{}'.format(self.img_name, index, IMG_FORMAT)
            new_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + img_name))
            self.panels[0].configure(image=new_img)
            self.panels[0].image = new_img
            self.panels[1].configure(image=new_img)
            self.panels[1].image = new_img

            if(index < 14):
                Timer(0.5, lambda: preview_inner(index+1)).start()
            else:
                self.update_images()

        preview_inner(0)


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

    def set_test_image_side(self, side):
        """Configure the LFImage to use the given panels for display.

        :param panels: 
        """
        self.test_image_side = side