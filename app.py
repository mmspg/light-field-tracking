#   app.py
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

from LFImage import LFImage
from TestSession import TestSession
from helper import Helper

# ---------------
# -- MAIN CODE --
# ---------------

images = []

# Add the images to be tested here
images.append(LFImage("I01R1"))
images.append(LFImage("I02R2"))
images.append(LFImage("I04R3"))

question = "How would you rate the impairment of the test image compared to the reference image?"
answers = [1, 2, 3, 4, 5]
answers_description = ["Very annoying",
                       "Annoying",
                       "Slightly annoying",
                       "Perceptible, but not annoying",
                       "Imperceptible"]

TestSession(images, question, answers, answers_description,
            show_preview=True, preload_images=True,
            assessment_method= Helper.IQA.DOUBLE_STIMULUS, test_image_side=Helper.Side.LEFT)
