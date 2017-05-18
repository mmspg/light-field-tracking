from LFImage import LFImage
from TestSession import TestSession
from helper import Side

###############
## MAIN CODE ##
###############

images = [None] * 2
images[0] = LFImage("I01R3", nb_img_x=15, nb_img_y=15, nb_img_depth=11, test_img_padding=1)
images[1] = LFImage("I02R3", nb_img_x=15, nb_img_y=15, nb_img_depth=11, test_img_padding=1)
# images[2] = LFImage("I04R3", nb_img_x=15, nb_img_y=15, nb_img_depth=11, test_img_padding=1)
# images[3] = LFImage("I09R3", nb_img_x=15, nb_img_y=15, nb_img_depth=11, test_img_padding=1)
# images[4] = LFImage("I10R3", nb_img_x=15, nb_img_y=15, nb_img_depth=11, test_img_padding=1)

question = "How would you rate the impairment of the test image (left) compared to the reference image (right)?"
answers = [1, 2, 3, 4, 5]
answers_description = ["Very annoying",
                       "Annoying",
                       "Slightly annoying",
                       "Perceptible, but not annoying",
                       "Imperceptible"]

TestSession(images, question, answers, answers_description, show_preview=False, preload_images=False, test_image_side=Side.RIGHT)
