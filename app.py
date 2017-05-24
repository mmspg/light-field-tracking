from LFImage import LFImage
from TestSession import TestSession
from helper import Helper

###############
## MAIN CODE ##
###############

images = []
images.append(LFImage("I01R1", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I02R1", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I04R1", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I09R1", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I10R1", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))

images.append(LFImage("I01R2", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I02R2", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I04R2", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I09R2", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I10R2", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))

images.append(LFImage("I01R3", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I02R3", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I04R3", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I09R3", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))
images.append(LFImage("I10R3", nb_img_x=9, nb_img_y=9, nb_img_depth=11, top_left=(3,3)))

question = "How would you rate the impairment of the test image (left) compared to the reference image (right)?"
answers = [1, 2, 3, 4, 5]
answers_description = ["Very annoying",
                       "Annoying",
                       "Slightly annoying",
                       "Perceptible, but not annoying",
                       "Imperceptible"]

TestSession(images, question, answers, answers_description,
            show_preview=False, preload_images=True, test_image_side=Helper.Side.RIGHT)
