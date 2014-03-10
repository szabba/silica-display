# -*- coding: utf-8 -*-

__all__ = ['Cam']


import numpy
from pyglet import gl


class Cam(object):
    """The camera"""

    def __init__(self, config):

        self.__config = config

        self.__matrix = numpy.eye(4)
        self.__gl_matrix = (16 * gl.GLfloat)()
        self.__recalc = True

    def recalculate(self):
        """C.recalculate()

        Recalculate the matrix, if necessary.
        """

        if not self.__recalc:
            return

        for i, elem in enumerate(self.__matrix.flat):

            self.__gl_matrix[i] = elem

    def matrix(self):
        """C.matrix() -> camera matrix"""

        self.recalculate()

        return self.__matrix

    def gl_matrix(self):
        """C.gl_matrix() -> camera matrix as ctypes array"""

        self.recalculate()

        return self.__gl_matrix
