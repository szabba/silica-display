# -*- coding: utf-8 -*-

import math
import numbers


class Vector(object):
    """A 3D vector in some Cartesian basis"""

    def __init__(self, x=0, y=0, z=0):

        if isinstance(x, numbers.Integral):
            x = float(x)

        if isinstance(y, numbers.Integral):
            y = float(y)

        if isinstance(z, numbers.Integral):
            z = float(z)

        self.x, self.y, self.z = x, y, z

    def __eq__(self, o):

        return self.x == o.x and self.y == o.y and self.z == o.z

    def __repr__(self):

        return "Vector(%s, %s, %s)" % (self.x, self.y, self.z)

    def __add__(self, o):

        return Vector(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):

        return self + (-o)

    def __mul__(self, o):

        if isinstance(o, numbers.Number):

            return Vector(self.x * o, self.y * o, self.z * o)

        return NotImplemented

    def __rmul__(self, o):

        if isinstance(o, numbers.Number):

            return self.__mul__(o)

        return NotImplemented

    def __div__(self, o):

        if isinstance(o, numbers.Number):

            return self * (1 / o)

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

    def __neg__(self):

        return Vector(-self.x, -self.y, -self.z)

    def __invert__(self):

        return -self

    def __abs__(self):

        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit(self):
        """V.unit() -> unit vector parallel to V and pointing in the same
        direction
        """

        return self / abs(self)

    def decompose(self, direction):
        """V.decompose(direction) -> parallel, orthogonal

        Decomposes V into the part parallel and orthogonal to direction (another Vector).
        """

        direction = direction.unit()

        parallel = self.dot(direction) * direction
        orthogonal = self - parallel

        return parallel, orthogonal

    def rotate(self, axis, angle):
        """V.rotate(axis, angle) -> rotated vector

        Rotates V to the right around the axis direction by the given angle.
        """

        parallel, orthogonal = self.decompose(axis)

        return parallel + abs(orthogonal) * (
                math.cos(angle) * orthogonal.unit() +
                math.sin(angle) * axis.unit().cross(orthogonal.unit()))
