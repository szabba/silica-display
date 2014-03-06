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

        self.__normal_array = self.__normals(
                self.__position_array)

    def __positions(self):
        """A.__positions() -> ctypes array of gl.GLfloat

        Vertex positions.
        """

        positions = numpy.zeros((
            Axes.AXIS_COUNT,
            Axes.TRIANGLES_PER_AXIS,
            VERTICES_PER_TRIANGLE,
            COORDINATES_PER_VERTEX))

        for t_ix in range(Axes.TRIANGLES_PER_AXIS):

            positions[0][t_ix][0] = [0, 0, 0]
            positions[0][t_ix][1] = [
                    1,
                    -1 if t_ix in (1, 2, 5, 6) else 1,
                    -1 if t_ix in (2, 3, 6, 7) else 1]

            t_ix_next_wrap = (t_ix + 1) % Axes.TRIANGLES_PER_AXIS

            positions[0][t_ix][2] = [
                    1,
                    -1 if t_ix_next_wrap in (1, 2, 5, 6) else 1,
                    -1 if t_ix_next_wrap in (2, 3, 6, 7) else 1]

        return positions

    def __normals(self, positions):
        """A.__normals(positions) -> ctypes array of gl.GLfloat

        Triangle normals.
        """

        positions = numpy.array(positions)

        positions.reshape(
                (-1, VERTICES_PER_TRIANGLE, COORDINATES_PER_VERTEX))

        TRIANGLES = positions.shape[0]

        normals = numpy.zeros(positions.shape)

        for i in range(TRIANGLES):

                edge1 = positions[i][0] - positions[i][1]
                edge2 = positions[i][1] - positions[i][2]

                normal = numpy.cross(edge1, edge2)

                normal /= numpy.sqrt(numpy.dot(normal, normal))

                normals[i,:] = normal

        return normals

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

        gl.glEnableVertexAttribArray(self.__position)
        gl.glVertexAttribPointer(
                self.__position, COORDINATES_PER_VERTEX,
                gl.GL_FLOAT, gl.GL_FALSE, 0,
                self.__position_array.ctypes.data_as(
                       c.POINTER(gl.GLfloat)))

        gl.glEnableVertexAttribArray(self.__normal)
        gl.glVertexAttribPointer(
                self.__normal, COORDINATES_PER_NORMAL,
                gl.GL_FLOAT, gl.GL_FALSE, 0,
                self.__normal_array.ctypes.data_as(
                       c.POINTER(gl.GLfloat)))

        gl.glUseProgram(0)
