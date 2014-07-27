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
