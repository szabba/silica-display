# -*- coding: utf-8 -*-

import numbers


class Vector(object):
    """A 3D vector in some Cartesian basis"""

    def __init__(self, x, y, z):

        self.x, self.y, self.z = x, y, z

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
