# -*- coding: utf-8 -*-

__all__ = ['Transform', 'Product']

from pyglet import gl


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
