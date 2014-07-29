# -*- coding: utf-8 -*-

__all__ = ['Axes']


import math
import ctypes as c

import numpy
from pyglet import gl

from constants import *
from utils import *
import shaders
import transform
import cube


class SquashZ(transform.Transform):
    '''Adjust the range of z coordinates, so that the axes won't get cut off by
    the clipping planes.
    '''

    def __init__(self, config):

        super(SquashZ, self).__init__()

        width, height = config.axes_size()
        scale = config.axes_scale()

        width *= scale
        height *= scale

        # The length of the longest diagonal of an axis indicator
        diagonal = math.sqrt(2 * math.pow(width, 2) + math.pow(height, 2))

        self.__z_scale = 1 / diagonal

    def calculate(self):

        squash = numpy.eye(4)
        squash[2, 2] = self.__z_scale

        self.set_matrix(squash)


class Axes(object):
    """The axis orientation indicators"""

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

        transforms['axis_total'] = axis_total = transform.Product()
        axis_total.add_factor(transforms['axis_shift'])
        axis_total.add_factor(transforms['project'])
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

        scale = self.__config.axes_scale()
        width, height = self.__config.axes_size()
        width *= scale
        height *= scale

        positions[0, :, :, :, 0] *= height
        positions[0, :, :, :, 1] *= width
        positions[0, :, :, :, 2] *= width

        positions[0, :, :, :, 1] -= width
        positions[0, :, :, :, 2] -= width

        positions[1, :, :, :, 0] *= width
        positions[1, :, :, :, 1] *= height
        positions[1, :, :, :, 2] *= width

        positions[1, :, :, :, 0] -= width
        positions[1, :, :, :, 2] -= width

        positions[2, :, :, :, 0] *= width
        positions[2, :, :, :, 1] *= width
        positions[2, :, :, :, 2] *= height

        positions[2, :, :, :, 0] -= width
        positions[2, :, :, :, 1] -= width

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
