#   LFImage.py
#   lf-tracking
#   Created by Tanguy Albrici under the supervision of Irene Viola
#
#  Copyright (C) 2017 ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland
#  Multimedia Signal Processing Group
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import datetime
from threading import Timer
import threading

from PIL import Image, ImageTk

from SubapertureImage import SubapertureImage
from helper import IMG_PATH_PREFIX, IMG_FORMAT, f_tracking, clamp, Helper


class LFImage:
    """"Represents a light-field image."""

    def __init__(self, img_name, nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3, 3), base_img=None, focus_depth=None, unit=20):
        """Initializes a light-field image.
        
        :param img_name: The name of the image (i.e. of the folder containing all its image files).
        :param nb_img_x: The number of images in the x-axis.
        :param nb_img_y: The number of images in the y-axis.
        :param nb_img_depth: The number of depth images (i.e. z-axis)
        :param top_left: The coordinates of the top-left viewpoint
        :param base_img: The Point representing the first image to display.
                         If it is None, the middle center image is taken.
        :param focus_depth: The initial depth that should be in focus.
        :param unit: The number of pixels one should move the mouse to switch to another viewpoint.
        """

        self.img_name = img_name
        self.reference_img_name = img_name.split("R")[0] + "R0"
        self.nb_img_x = nb_img_x
        self.nb_img_y = nb_img_y
        self.nb_img_depth = nb_img_depth
        self.top_left = top_left

        if base_img is None:
            # Take the center perspective image
            self.base_img = SubapertureImage(top_left[0] + (nb_img_x // 2),
                                             top_left[1] + (nb_img_y // 2),
                                             focus_depth)
        else:
            self.base_img = base_img

        self.unit = unit

        self.test_images = [[None for _ in range(top_left[0] + nb_img_x)] for _ in range(top_left[1] + nb_img_y)]
        self.test_images_refocus = [None for _ in range(nb_img_depth)]
        self.ref_images = [[None for _ in range(top_left[0] + nb_img_x)] for _ in range(top_left[1] + nb_img_y)]
        self.ref_images_refocus = [None for _ in range(nb_img_depth)]

        self.cur_img = None
        self.next_img = self.base_img
        self.depth_map = Image.open("{}/depth_map/{}.{}".format(IMG_PATH_PREFIX, self.reference_img_name, IMG_FORMAT)).load()
        self.click_pos = (0, 0)
        self.prev_time = 0
        self.cur_time = 0
        self.panels = None
        self.test_image_side = None
        self.is_preview_running = False
        self.is_loaded = False

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
        if not self.is_preview_running:
            diff_x = self.click_pos[0] - move_pos[0]
            diff_y = self.click_pos[1] - move_pos[1]

            img_diff_x = int(round(diff_x / float(self.unit)))
            img_diff_y = int(round(diff_y / float(self.unit)))

            next_img_x = clamp(self.base_img.u + img_diff_x,
                               self.top_left[0],
                               self.top_left[0] + self.nb_img_x - 1)
            next_img_y = clamp(self.base_img.v + img_diff_y,
                               self.top_left[1],
                               self.top_left[1] + self.nb_img_y - 1)
            self.next_img = SubapertureImage(next_img_x, next_img_y, None)

            self.update_images()
            self.set_focus_slider_value(0)

    def refocus_to_depth(self, focus_depth):
        """Displays the image corresponding to the given focus depth.
        
        :param focus_depth: The depth to focus to image on.
        """
        if not self.is_preview_running:
            self.next_img = SubapertureImage(self.top_left[0] + self.nb_img_x // 2,
                                             self.top_left[1] + self.nb_img_y // 2,
                                             int(focus_depth))
            self.update_images()

            self.set_focus_slider_value(focus_depth)

    def refocus_to_point(self, event):
        """Refocus the current image on the given point using the depth map

        :param event: The event that triggered the refocusing and contains the point coordinates
        """
        depth_map_value = self.depth_map[event.x, event.y] / 255
        focus_depth = round(depth_map_value * (self.nb_img_depth - 1))
        self.refocus_animation(focus_depth)

    def refocus_animation(self, depth):
        """Animates the refocusing to the given depth in a smooth transition
        
        :param depth: The final depth at the end of the animation
        """
        if self.cur_img.focus_depth is not None:
            if self.cur_img.focus_depth != depth:
                depth_delta = 1 if (depth - self.cur_img.focus_depth > 0) else -1
                new_depth = self.cur_img.focus_depth + depth_delta
                self.refocus_to_depth(new_depth)

                if new_depth != depth:
                    Timer(0.01, lambda: self.refocus_animation(depth)).start()
        else:
            self.refocus_to_depth(depth)

    def set_focus_slider_value(self, value):
        Helper.is_focus_slider_enabled = False
        Helper.focus_slider.set(value)

    def update_images(self):
        """Updates the image displayed according to the next_img attribute"""

        if self.next_img != self.cur_img:
            if not self.is_preview_running:
                self.close_img()

            self.cur_img = self.next_img

            if self.cur_img.focus_depth is None:
                # Display a normal image
                new_test_img = self.test_images[self.cur_img.u][self.cur_img.v]
                new_ref_img = self.ref_images[self.cur_img.u][self.cur_img.v]

            else:
                # Display a refocused image
                new_test_img = self.test_images_refocus[self.cur_img.focus_depth]
                new_ref_img = self.ref_images_refocus[self.cur_img.focus_depth]

            test_img_name, ref_img_name = self.get_cur_img_names()

            # Load the images if they were not already loaded
            if new_test_img is None:
                new_test_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + test_img_name))
                self.test_images[self.cur_img.u][self.cur_img.v] = new_test_img
            if new_ref_img is None and len(self.panels) == 2:
                # The reference image is only needed for the double stimulus method
                new_ref_img = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + ref_img_name))
                self.ref_images[self.cur_img.u][self.cur_img.v] = new_ref_img

            if len(self.panels) == 2: # Double stimulus
                # Set the test and reference image on the correct side (left=0, right=1)
                self.panels[self.test_image_side.value].configure(image=new_test_img)
                self.panels[self.test_image_side.value].image = new_test_img
                self.panels[(self.test_image_side.value + 1) % 2].configure(image=new_ref_img)
                self.panels[(self.test_image_side.value + 1) % 2].image = new_ref_img
            elif len(self.panels) == 1: # Single stimulus
                self.panels[0].configure(image=new_test_img)
                self.panels[0].image = new_test_img

    def load_images(self, assessment_method):
        def callback():

            # Load normal images
            for x in range(self.top_left[0], self.top_left[0] + self.nb_img_x):
                for y in range(self.top_left[1], self.top_left[1] + self.nb_img_y):
                    test_img_name = '{}/{:03}_{:03}.{}'.format(self.img_name, x, y, IMG_FORMAT)
                    ref_img_name = '{}/{:03}_{:03}.{}'.format(self.reference_img_name, x, y, IMG_FORMAT)

                    self.test_images[x][y] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + test_img_name))

                    # The reference image is only needed for the double stimulus method
                    if assessment_method is Helper.IQA.DOUBLE_STIMULUS:
                        self.ref_images[x][y] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + ref_img_name))

            # Load refocused images
            for depth in range(self.nb_img_depth):
                test_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.img_name, self.base_img.u, self.base_img.v,
                                                                 depth, IMG_FORMAT)
                ref_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.reference_img_name, self.base_img.u, self.base_img.v,
                                                                depth, IMG_FORMAT)
                self.test_images_refocus[depth] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + test_img_name))
                # The reference image is only needed for the double stimulus method
                if assessment_method is Helper.IQA.DOUBLE_STIMULUS:
                    self.ref_images_refocus[depth] = ImageTk.PhotoImage(Image.open(IMG_PATH_PREFIX + ref_img_name))

            self.is_loaded = True
            # Hide loading message
            if Helper.fullscreen_msg is not None:
                Helper.fullscreen_msg.pack_forget()

        t = threading.Thread(target=callback)
        t.start()

    def preview(self, time_per_image=0.1, time_per_image_refocus=0.25, start=3, end=11):
        """Display a preview of the LF image by going through a predefined subset of the sub-aperture images.
           It first shows the perspective images in alternate scanner order, starting with the coordinate 
           (start, start) and ending with (end, end). Then, it shows the refocused images by going from the foreground
           to the background and back to the foreground.
        """

        def preview_inner(index, preview_images):
            """Displays the images given by 'preview_images', starting at position 'index'.
            :param index: Index of the first image to display.
            :param preview_images: List of images to show in the preview.
            """
            self.next_img = preview_images[index]
            self.update_images()

            if index + 1 < len(preview_images):
                timeout = time_per_image if (self.next_img.focus_depth is None) else time_per_image_refocus
                Timer(timeout, lambda: preview_inner(index + 1, preview_images)).start()
            else:
                # End the preview and display the base image
                self.is_preview_running = False
                self.next_img = self.base_img
                # self.cur_time = 0
                self.update_images()

        # List of images ordered for the preview
        preview_images_list = []

        next_img = SubapertureImage(start, start, None)
        delta_x = 1

        # Set the order of images for the preview
        for y in range(start, end + 1):
            next_img = SubapertureImage(next_img.u, y, None)
            preview_images_list.append(next_img)

            for _ in range(start, end):
                next_img = SubapertureImage(next_img.u + delta_x, next_img.v, None)
                preview_images_list.append(next_img)

            delta_x = -delta_x

        for d in range(0, 2 * self.nb_img_depth - 1):
            depth = d if (d < self.nb_img_depth) else 2 * self.nb_img_depth - 2 - d
            next_img = SubapertureImage(self.base_img.u, self.base_img.v, depth)
            preview_images_list.append(next_img)

        # Start the preview
        self.is_preview_running = True
        preview_inner(0, preview_images_list)

    def close_img(self):
        """Perform actions necessary when an image is replaced by another.
        
        This method is used to write the end time and on-screen time in the tracking.txt file.
        """
        self.prev_time = self.cur_time
        self.cur_time = datetime.datetime.now()

        if self.prev_time != 0:
            onscreen = self.cur_time - self.prev_time

            test_img_name, _ = self.get_cur_img_names()

            to_write = "{}  start: {}  end: {}  on-screen: {}\n".format(
                test_img_name,
                self.prev_time.strftime('%H:%M:%S.%f'),
                self.cur_time.strftime('%H:%M:%S.%f'),
                onscreen
            )

            f_tracking.write(to_write)

    def get_cur_img_names(self):
        """Returns a tuple containing the name of the current test image and of the current reference image"""

        if self.cur_img.focus_depth is None:
            # Normal image
            test_img_name = '{}/{:03}_{:03}.{}'.format(self.img_name, self.cur_img.u, self.cur_img.v, IMG_FORMAT)
            ref_img_name = '{}/{:03}_{:03}.{}'.format(self.reference_img_name, self.cur_img.u, self.cur_img.v,
                                                      IMG_FORMAT)

        else:
            # Refocused image
            test_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.img_name, self.cur_img.u, self.cur_img.v,
                                                             self.cur_img.focus_depth, IMG_FORMAT)
            ref_img_name = '{}/{:03}_{:03}_{:03}.{}'.format(self.reference_img_name, self.cur_img.u, self.cur_img.v,
                                                            self.cur_img.focus_depth, IMG_FORMAT)

        return test_img_name, ref_img_name

    def clear_memory(self):
        """Dereference the arrays of images loaded so that they are cleared by the garbage collector"""

        self.ref_images = None
        self.ref_images_refocus = None
        self.test_images = None
        self.test_images_refocus = None
        self.is_loaded = False

    def set_panels(self, panels):
        """Configure the LFImage to use the given panels for display.
        
        :param panels: Panels on which the images will be displayed
        """
        self.panels = panels

    def set_test_image_side(self, side):
        """Set the side on which the test image should be displayed.

        :param side: Side on which the test image should be displayed.
        """
        self.test_image_side = side
