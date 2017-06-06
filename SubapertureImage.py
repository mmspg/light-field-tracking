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
