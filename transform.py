# -*- coding: utf-8 -*-

__all__ = ['Transform']


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
