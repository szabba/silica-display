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

        self.__ratio = numpy.eye(4)

        self.__s = config.init_scale()
        self.__scale = numpy.eye(4)
        for i in range(3):
            self.__scale[i, i] = self.__s

    def recalculate(self):
        """C.recalculate()

        Recalculate the matrix, if necessary.
        """

        if not self.__recalc:
            return

        self.__matrix[:] = self.__ratio.dot(self.__scale)

        for i, elem in enumerate(self.__matrix.flat):

            self.__gl_matrix[i] = elem

        self.__recalc = False

    def matrix(self):
        """C.matrix() -> camera matrix"""

        self.recalculate()

        return self.__matrix

    def gl_matrix(self):
        """C.gl_matrix() -> camera matrix as ctypes array"""

        self.recalculate()

        return self.__gl_matrix

    def on_resize(self, width, height):

        self.__recalc = True

        self.__ratio[0, 0] = float(height) / float(width)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        self.__recalc = True

        if scroll_y < 0:
            multiplier = (1 - self.__config.zoom_speed()) * abs(scroll_y)
        else:
            multiplier = (1 + self.__config.zoom_speed()) * abs(scroll_y)

        for i in range(3):
            self.__scale[i, i] *= multiplier
