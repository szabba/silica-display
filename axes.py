# -*- coding: utf-8 -*-

__all__ = ['Axes']


import ctypes as c

import numpy
from pyglet import gl

from constants import *
import shaders


class Axes(object):
    """The glass (or it's visible part)"""

    AXIS_COUNT = 3
    TRIANGLES_PER_AXIS = 8

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.build_program('axes')

        self.__sun = self.__uniform_location('sun')
        self.__ambient = self.__uniform_location('ambient')
        self.__diffuse = self.__uniform_location('diffuse')
        self.__colors = self.__uniform_location('colors')

        self.__position = self.__attritbute_location('position')
        self.__normal = self.__attritbute_location('normal')
        self.__color_no = self.__attritbute_location('color_no')

        self.__axis_colors = (gl.GLfloat * (
            RGB_COMPONENTS * Axes.AXIS_COUNT))(
                    *[
                        1, 0, 0,
                        0, 1, 0,
                        0, 0, 1])

        self.__position_array = self.__positions()

    def __positions(self):
        """A.__positions() -> ctypes array of gl.GLfloat

        Vertex positions.
        """

        positions = numpy.zeros((
            Axes.AXIS_COUNT,
            Axes.TRIANGLES_PER_AXIS,
            VERTICES_PER_TRIANGLE,
            COORDINATES_PER_VERTEX))

        return positions.ctypes.data_as(
                c.POINTER(gl.GLfloat))

    def __uniform_location(self, name):
        """A.__uniform_location(name) -> location

        The OpenGL location of a uniform value.
        """

        return gl.glGetUniformLocation(
                self.__program, name)

    def __attritbute_location(self, name):
        """A.__attritbute_location(name) -> location

        The OpenGL location of an attribute.
        """

        return gl.glGetAttribLocation(
                self.__program, name)

    def on_draw(self):

        gl.glUseProgram(self.__program)

        gl.glUniform3fv(
                self.__sun, 1,
                self.__config.sun_direction())

        gl.glUniform1f(
                self.__ambient,
                self.__config.axis_ambient())

        gl.glUniform1f(
                self.__diffuse,
                self.__config.axis_diffuse())

        gl.glUniform3fv(
                self.__colors, 1,
                self.__axis_colors)

        gl.glUseProgram(0)
