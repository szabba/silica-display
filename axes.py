# -*- coding: utf-8 -*-

__all__ = ['Axes']


import ctypes as c

import numpy
from pyglet import gl

from constants import *
from utils import *
import shaders
import transform
import cube


AXIS_HEIGHT = 8
AXIS_WIDTH = 1


class Axes(object):
    """The glass (or it's visible part)"""

    TRIANGLES_PER_AXIS = 8

    def __init__(self, config, transforms, window):

        self.__config = config

        self.create_transforms(transforms, window)
        self.__total_transform = transforms['axis_total']
        self.__shift = transforms['axis_shift']

        self.__program = shaders.Program('axes')

        self.__sun = self.__program.uniform(
                'sun',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__ambient = self.__program.uniform(
                'ambient',
                shaders.GLSLType(gl.GLfloat))

        self.__diffuse = self.__program.uniform(
                'diffuse',
                shaders.GLSLType(gl.GLfloat))

        self.__camera = self.__program.uniform(
                'camera',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Matrix(4)))

        self.__program.attribute(
                'position',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'normal',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'color',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__triangles = self.__program.triangle_list(
                AXIS_COUNT * cube.TRIANGLES_PER_CUBE)

        ps, ns = self.__positions_and_normals()

        self.__triangles.from_arrays(dict(
            color=self.__colors(ps),
            normal=ns, position=ps))

    def create_transforms(self, transforms, window):
        """A.create_transforms(transforms, window)

        Create all the transforms necessary for proper axis rendering.
        """

        transforms['axis_shift'] = transform.Translate(
                *self.translation_from_win_size(*window.get_size()))
        axis_scale = transform.Scale(self.__config.axes_scale())

        transforms['axis_total'] = axis_total = transform.Product()
        axis_total.add_factor(transforms['axis_shift'])
        axis_total.add_factor(transforms['project'])
        axis_total.add_factor(axis_scale)
        axis_total.add_factor(transforms['rot'])

    def translation_from_win_size(self, width, height):
        """A.translation_from_win_size(width, height) -> (dx, dy, dz)

        Calculates the proper translation the axes must undergo through the
        'axis_shift' transform based on the window size in pixels.
        """

        from_left, from_bottom = self.__config.axes_position()

        dx = (-width + from_left) / width
        dy = (-height + from_bottom) / height

        return (dx, dy, 0)

    def __positions_and_normals(self):
        """A.__positions_and_normals() -> positions, normals"""

        positions = cube.CUBE_FACES.repeat(
                AXIS_COUNT
        ).reshape(
                cube.CUBE_FACES.shape + (AXIS_COUNT, )
        )
        positions = numpy.rollaxis(positions, -1)

        positions[0, :, :, :, 0] *= AXIS_HEIGHT
        positions[0, :, :, :, 1] -= AXIS_WIDTH
        positions[0, :, :, :, 2] -= AXIS_WIDTH

        positions[1, :, :, :, 0] -= AXIS_WIDTH
        positions[1, :, :, :, 1] *= AXIS_HEIGHT
        positions[1, :, :, :, 2] -= AXIS_WIDTH

        positions[2, :, :, :, 0] -= AXIS_WIDTH
        positions[2, :, :, :, 1] -= AXIS_WIDTH
        positions[2, :, :, :, 2] *= AXIS_HEIGHT

        normals = cube.CUBE_NORMALS.repeat(
                AXIS_COUNT
        ).reshape(
                cube.CUBE_NORMALS.shape + (AXIS_COUNT, )
        )
        normals = numpy.rollaxis(normals, -1)

        return positions, normals

    def __colors(self, positions):
        """A.__colors(positions) -> ctypes array of gl.GLfloats

        Colors.
        """

        colors = numpy.zeros(positions.size)

        colors = colors.reshape((AXIS_COUNT, -1, RGB_COMPONENTS))

        color = [1, 0, 0]
        for i in range(AXIS_COUNT):

            colors[i, :] = color
            color.insert(0, color.pop(-1))

        return colors

    def on_resize(self, width, height):

        self.__shift.set_r(
                *self.translation_from_win_size(width, height))

    def on_draw(self):

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        with self.__triangles as triangles:

            self.__camera.clear()
            self.__camera.add(*self.__total_transform.gl_matrix())
            self.__camera.set()

            if not self.__sun.filled():
                self.__sun.add(*self.__config.sun_direction())
            self.__sun.set()

            if not self.__ambient.filled():
                self.__ambient.add(self.__config.axis_ambient())
            self.__ambient.set()

            if not self.__diffuse.filled():
                self.__diffuse.add(self.__config.axis_diffuse())
            self.__diffuse.set()

            triangles.draw()
