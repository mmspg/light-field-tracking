
#   SubapertureImage.py
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

class SubapertureImage:
    """"Represents a sub-aperture image via its coordinates"""

    def __init__(self, u, v, focus_depth):
        """Initializes a sub-aperture image.

        :param x:
        :param y:
        :param focus_depth:
        """
        self.u = u
        self.v = v
        self.focus_depth = focus_depth

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "({}, {}, )".format(self.u, self.v, self.focus_depth)
