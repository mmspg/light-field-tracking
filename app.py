import tkinter as tk

from LFImage import LFImage
from TestSession import TestSession

###############
## MAIN CODE ##
###############

images = [None] * 6
images[0] = LFImage("Bikes", 15, 15, 11)
images[1] = LFImage("Danger_de_Mort", 15, 15, 11)
images[2] = LFImage("Flowers", 15, 15, 11)
images[3] = LFImage("Fountain_&_Vincent_2", 15, 15, 11)
images[4] = LFImage("Friends_1", 15, 15, 11)
images[5] = LFImage("Stone_Pillars_Outside", 15, 15, 11)

question = "How would you rate the impairment of the test image (left) compared to the reference image (right)?"
answers = [1, 2, 3, 4, 5]
answers_description = ["Very annoying",
                       "Annoying",
                       "Slightly annoying",
                       "Perceptible, but not annoying",
                       "Imperceptible"]

TestSession(images, question, answers, answers_description, show_preview=False)
