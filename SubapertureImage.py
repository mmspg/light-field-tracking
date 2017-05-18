class SubapertureImage:
    """"Represents a sub-aperture image via its coordinates"""

    def __init__(self, x, y, focus_depth):
        self.x = x
        self.y = y
        self.focus_depth = focus_depth

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "({}, {}, )".format(self.x, self.y, self.focus_depth)
