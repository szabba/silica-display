# -*- coding: utf-8 -*-

__all__ = ['Axes']


import ctypes as c

import numpy
from pyglet import gl

from constants import *
from utils import *
import shaders
import cube


class Axes(object):
    """The glass (or it's visible part)"""

    TRIANGLES_PER_AXIS = 8

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

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

    def __positions_and_normals(self):
        """A.__positions_and_normals() -> positions, normals"""

        positions = cube.CUBE_FACES.repeat(
                AXIS_COUNT
        ).reshape(
                cube.CUBE_FACES.shape + (AXIS_COUNT, )
        )
        positions = numpy.rollaxis(positions, -1)

        positions[0, :, :, :, 0] *= 8
        positions[0, :, :, :, 1] -= 1
        positions[0, :, :, :, 2] -= 1

        positions[1, :, :, :, 0] -= 1
        positions[1, :, :, :, 1] *= 8
        positions[1, :, :, :, 2] -= 1

        positions[2, :, :, :, 0] -= 1
        positions[2, :, :, :, 1] -= 1
        positions[2, :, :, :, 2] *= 8

        normals = cube.CUBE_NORMALS.repeat(
                AXIS_COUNT
        ).reshape(
                cube.CUBE_NORMALS.shape + (AXIS_COUNT, )
        )
        normals = numpy.rollaxis(normals, -1)

        return positions, normals

    def __positions(self):
        """A.__positions() -> ctypes array of gl.GLfloat

        Vertex positions.
        """

        positions = numpy.zeros((
            AXIS_COUNT,
            Axes.TRIANGLES_PER_AXIS,
            VERTICES_PER_TRIANGLE,
            COORDINATES_PER_VERTEX))

        for t_ix in range(Axes.TRIANGLES_PER_AXIS):

            positions[0][t_ix][0] = [0, 0, 0] if t_ix in (0, 1, 2, 3) else [7, 0, 0]
            positions[0][t_ix][1] = [
                    1,
                    -1 if t_ix in (1, 2, 5, 6) else 1,
                    -1 if t_ix in (2, 3, 6, 7) else 1]

            t_ix_next_wrap = (t_ix + 1) % Axes.TRIANGLES_PER_AXIS

            positions[0][t_ix][2] = [
                    1,
                    -1 if t_ix_next_wrap in (1, 2, 5, 6) else 1,
                    -1 if t_ix_next_wrap in (2, 3, 6, 7) else 1]

        shift = numpy.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0]])

        for axis in range(1, AXIS_COUNT):
            for t_ix in range(Axes.TRIANGLES_PER_AXIS):
                for v_ix in range(VERTICES_PER_TRIANGLE):

                    v = shift.dot(positions[axis - 1][t_ix][v_ix])
                    positions[axis][t_ix][v_ix] = v

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

    def on_draw(self):

        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        with self.__triangles as triangles:

            self.__camera.clear()
            self.__camera.add(*self.__cam.gl_matrix())
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
