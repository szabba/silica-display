# -*- coding: utf-8 -*-

__all__ = ['Cam']


import math

import numpy
from pyglet import gl
from pyglet.window import mouse


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

        self.__phi = config.init_phi()
        self.__rot_z = numpy.eye(4)

        self.__theta = config.init_theta()
        self.__rot_y = numpy.eye(4)

    def recalculate(self):
        """C.recalculate()

        Recalculate the matrix, if necessary.
        """

        if not self.__recalc:
            return

        self.__matrix[:] = numpy.eye(4)

        for transform in [
                self.__ratio,
                self.__rot_y,
                self.__rot_z,
                self.__scale]:

            self.__matrix[:] = numpy.dot(self.__matrix, transform)

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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        self.__recalc = True

        if buttons == mouse.LEFT:

            self.__phi += dx * self.__config.rot_z_speed()

            while self.__phi < 0:
                self.__phi += 2 * math.pi

            while self.__phi > 2 * math.pi:
                self.__phi -= 2 * math.pi

            self.__rot_z[0, 0] = self.__rot_z[1, 1] = numpy.cos(self.__phi)
            self.__rot_z[1, 0] = numpy.sin(self.__phi)
            self.__rot_z[0, 1] = -self.__rot_z[1, 0]

            self.__theta += dy * self.__config.rot_z_speed()

            while self.__theta < -math.pi / 2:
                self.__theta = -math.pi / 2

            while self.__theta > math.pi / 2:
                self.__theta = math.pi / 2

            self.__rot_y[0, 0] = self.__rot_y[2, 2] = numpy.cos(self.__theta)
            self.__rot_y[2, 0] = numpy.sin(self.__theta)
            self.__rot_y[0, 2] = -self.__rot_y[2, 0]
