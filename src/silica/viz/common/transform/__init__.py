# -*- coding: utf-8 -*-

__all__ = [
    'Transform', 'Product', 'BasicAxisRotation', 'Scale',
    'Translate', 'FlipHandedness', 'CameraGeometry',
    'Foreshortening', 'AspectRatio', 'LookAt']


import math

import numpy
from pyglet import gl

from silica.viz.common.constants import AXIS_COUNT
from silica.viz.common import vector


class Transform(object):

    '''A linear transform of homogeneous coordinates.'''

    def __init__(self):

        self.__used_by = set()
        self.__matrix = None
        self.__gl_matrix = None

    def dirty(self):
        """T.dirty()

        Marks the transform as dirty, so that it will be recalculated next time
        the matrix is requested.
        """

        self.__matrix, self.__gl_matrix = None, None

        for user in self.__used_by:
            user.dirty()

    def add_user(self, user):
        """T.add_user(user)

        Add a transform that will cascadingly be made dirty when this one does.
        """

        self.__used_by.add(user)

    def set_matrix(self, matrix):
        """T.set_matrix(matrix)

        Sets the internal matrix. To be used by subclasses.
        """

        self.__matrix = matrix

    def calculate(self):
        """T.calculate()

        Calculate the internal numpy matrix.
        """

        raise NotImplementedError(
            'A transform.Transform subtype must implement a calculate method')

    def matrix(self):
        """T.matrix() -> the transform matrix as a numpy array"""

        if self.__matrix is None:
            self.calculate()

        return self.__matrix

    def gl_matrix(self):
        """T.gl_matrix() -> the matrix as a ctypes array ready for OpenGL"""

        if self.__gl_matrix is None:

            self.__gl_matrix = (gl.GLfloat * 16)()

            for i, elem in enumerate(self.matrix().flat):

                self.__gl_matrix[i] = elem

        return self.__gl_matrix

    def __mul__(self, o):

        if isinstance(o, Transform):

            product = Product()
            product.add_factor(self)
            product.add_factor(o)
            return product

        elif isinstance(o, vector.Vector):

            matrix = self.matrix()

            transformed = matrix.dot(
                numpy.array([[o.x], [o.y], [o.z], [1]]))

            return vector.Vector(
                transformed[0, 0],
                transformed[1, 0],
                transformed[2, 0])

        return NotImplemented


class Product(Transform):

    """A transform resulting from matrix multiplication of it's factors."""

    def __init__(self):

        super(Product, self).__init__()

        self.__factors = []

    def add_factor(self, factor):
        """P.add_factor(factor)

        Add a new factor to the product transform. The last one added ends up
        applied to the homogeneous coordinates first.
        """

        factor.add_user(self)
        self.__factors.append(factor)

    def calculate(self):
        """P.calculate()

        Multiplies the factor matrices first to last and stores as the result
        transform matrix.
        """

        mat = numpy.eye(4)
        for factor in self.__factors:
            mat = mat.dot(factor.matrix())

        self.set_matrix(mat)


class BasicAxisRotation(Transform):

    """Rotation around one of the basic axes."""

    def __init__(self, angle, axis):

        super(BasicAxisRotation, self).__init__()
        self.__angle, self.__axis = angle, axis

    def set_angle(self, angle):
        """BAR.set_angle(angle)

        Set the angle value.
        """

        self.__angle = angle
        self.dirty()

    def angle(self):
        """BAR.angle() -> angle"""

        return self.__angle

    def __trig_indices(self):
        """BAR.__trig_indices() -> up_left, up_right, down_left, down_right

        The indices at which the trig functions of the angle should be
        inserted.
        """

        ixes = [axis for axis in range(AXIS_COUNT) if axis != self.__axis]

        out = []
        for i in ixes:
            for j in ixes:
                out.append((i, j))

        return out

    def calculate(self):

        cos, sin = math.cos(self.__angle), math.sin(self.__angle)

        matrix = numpy.eye(4)
        for ix, value in zip(
                self.__trig_indices(),
                [cos, -sin, sin, cos]):

            matrix[ix] = value

        self.set_matrix(matrix)


class ChangeBasis(Transform):

    """A transform that changes vector coordinates from one Cartesian basis
    into another.
    """

    def __init__(self, e_0, e_1, e_2):

        super(ChangeBasis, self).__init__()
        self.set_basis(e_0, e_1, e_2)

    def basis(self):
        """CB.basis() -> tuple of three base vectors"""

        return self.__basis

    def set_basis(self, e_0, e_1, e_2, dirtify=True):
        """CB.set_basis(e_0, e_1, e_2)

        Sets the new output basis. The base vectors should be expressed in
        coordinates of the input basis.
        """

        self.__basis = e_0, e_1, e_2
        if dirtify:
            self.dirty()

    def calculate(self):

        e_0, e_1, e_2 = self.__basis

        start = numpy.array([
            [e_0.x, e_0.y, e_0.z, 0],
            [e_1.x, e_1.y, e_1.z, 0],
            [e_2.x, e_2.y, e_2.z, 0],
            [0,     0,     0, 1]])

        if self.__orthogonalize:

            orthogonal = numpy.eye(4)

            U, S, V = numpy.linalg.svd(start)
            orthogonal[:3, :3] = U.dot(V)[:3, :3]

            self.set_basis(
                vector.Vector(*orthogonal[0, :3]),
                vector.Vector(*orthogonal[1, :3]),
                vector.Vector(*orthogonal[2, :3]),
                dirtify=False)

            self.set_matrix(orthogonal)

        else:

            self.set_matrix(start)


class Scale(Transform):

    """A scaling transform"""

    def __init__(self, scale):

        super(Scale, self).__init__()
        self.__scale = scale

    def set_scale(self, scale):
        """S.set_scale(scale)

        Set the scaling factor.
        """

        self.__scale = scale
        self.dirty()

    def scale(self):
        """S.scale() -> scale"""

        return self.__scale

    def calculate(self):

        matrix = numpy.eye(4)
        matrix[:3, :3] *= self.__scale

        self.set_matrix(matrix)


class Translate(Transform):

    '''A translation by a 3D vector'''

    def __init__(self, x, y, z):

        super(Translate, self).__init__()
        self.__r = (x, y, z)

    def set_r(self, x, y, z):
        """T.set_r(x, y, z)

        Set the translation vector.
        """

        self.__r = (x, y, z)
        self.dirty()

    def r(self):
        """T.r() -> (x, y, z)

        The translation vector coordinates.
        """

        return self.__r

    def calculate(self):

        t = numpy.eye(4)
        t[:3, 3] = self.__r

        self.set_matrix(t)


class FlipHandedness(Transform):

    '''Flips handedness of the coordinate system by changing the sign of the
    given axis' coordinate.
    '''

    def __init__(self, axis):

        super(FlipHandedness, self).__init__()
        self.__axis = axis

    def calculate(self):

        flipH = numpy.eye(4)
        flipH[self.__axis, self.__axis] = -1

        self.set_matrix(flipH)


class CameraGeometry(object):

    '''The geometry of a camera.'''

    def __init__(self, d0, d):

        self.__d0 = d0
        self.__d = d

    def eye_distance_from_screen(self):
        """CG.eye_distance_from_screen() -> the distance of the eye point from the screen"""

        return self.__d0

    def sight_range_from_screen(self):
        """CG.sight_range_from_screen() -> how far away from the screen can we see?"""

        return self.__d


class Foreshortening(Transform):

    '''A foreshortening (perspective projection) transform'''

    def __init__(self, geometry):

        super(Foreshortening, self).__init__()
        self.__geometry = geometry

    def calculate(self):

        d0 = self.__geometry.eye_distance_from_screen()
        d = self.__geometry.sight_range_from_screen()

        foreshort = numpy.eye(4)

        foreshort[2, 2] = 1. / d0 + 2. / d
        foreshort[2, 3] = -1
        foreshort[3, 2] = 1. / d0

        self.set_matrix(foreshort)


class AspectRatio(Transform):

    '''Adjust x:y proportions to avoid distortion.'''

    def __init__(self, width, height):

        super(AspectRatio, self).__init__()

        self.__w, self.__h = width, height

    def set_size(self, width, height):
        """AR.set_size(width, height)

        Set the window size.
        """

        self.__w, self.__h = width, height
        self.dirty()

    def size(self):
        """AR.size() -> width, height

        Window size in pixels.
        """

        return self.__w, self.__h

    def calculate(self):

        aspect = numpy.eye(4)
        aspect[0, 0] = 2. / self.__w
        aspect[1, 1] = 2. / self.__h

        self.set_matrix(aspect)


class LookAt(Transform):

    '''Move the point from the middle of the screen to the middle of the
    visible area.
    '''

    def __init__(self, geometry, scale):

        super(LookAt, self).__init__()
        self.__geometry = geometry
        self.__scale = scale
        self.__scale.add_user(self)

    def calculate(self):

        d = self.__geometry.sight_range_from_screen()
        s = self.__scale.scale()

        look_at = numpy.eye(4)

        look_at[2, 2] = 1 / s
        look_at[2, 3] = -d / 2

        self.set_matrix(look_at)
