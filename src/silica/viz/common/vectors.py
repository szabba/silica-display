# -*- coding: utf-8 -*-

import numbers


class Vector(object):
    """A 3D vector in some Cartesian basis"""

    def __init__(self, x, y, z):

        self.x, self.y, self.z = x, y, z

    def __eq__(self, o):

        return self.x == o.x and self.y == o.y and self.z == o.z

    def __add__(self, o):

        if not isinstance(o, self.__class__.__name__):
            raise TypeError(
                    '%s should be a %s; vectors only add to vectors',
                    o, self.__class__.__name__)

        return Vector(self.x + o.x, self.y + o.y, self.z + o.z)

    def __mul__(self, o):

        if isinstance(o, numbers.Number):

            return Vector(self.x * o, self.y * o, self.z * o)

        return NotImplemented

    def dot(self, o):
        """V.dot(o) -> the dot product of V and o"""

        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o):
        """V.cross(o) -> the cross produt of V and o"""

        return Vector(
                self.y * o.z - self.z * o.y,
                self.z * o.x - self.x * o.z,
                self.x * o.y - self.y * o.x)
