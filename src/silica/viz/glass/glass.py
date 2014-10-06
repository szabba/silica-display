# -*- coding: utf-8 -*-

__all__ = ['Glass']

import os.path

import numpy
from pyglet import gl

from silica.viz.common import shaders
from silica.viz.common.grid.surface import SurfaceDataGenerator
from silica.viz.common.grid.load import (
        GridCubeLoader, Sizer,
        InclusionCondition, AndCondition, Slice3D)
from silica.viz.common.constants import *
from silica.viz.common.cube import *


def grid_lines(filename):
    """grid_lines(filename) -> iter

    Returns an iterator ranging over the lines of a grid file.
    """

    with open(filename) as grid_file:
        for line in grid_file:

            yield tuple(map(int, line.split(' ')))


class Sizer(Sizer):

    def __init__(self, size):
        self.__size = size

    def size(self):
        return self.__size


class ValueEqual(InclusionCondition):

    def __init__(self, value):
        self.__value = value

    def include(self, x, y, z, v):

        return v == self.__value


class Glass(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.Program('glass')

        self.__camera = self.__program.uniform(
                'camera',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Matrix(4)))

        self.__sun = self.__program.uniform(
                'sun',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__color = self.__program.uniform(
                'color',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__copy_shift = self.__program.uniform(
                'copy_shift',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'position',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'normal',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        includer = AndCondition(
                ValueEqual(1),
                Slice3D(*self.__config.limits()))

        with open(self.__config.grid_file()) as input_file:

            grid, cubes = GridCubeLoader(
                    input_file, includer,
                    Sizer(self.__config.grid_size())).load()

        surf_data_gen = SurfaceDataGenerator(grid)
        positions, normals = surf_data_gen.positions_and_normals(grid, cubes)

        SIDES = positions.shape[0]
        TRIANGLES = SIDES * TRIANGLES_PER_SQUARE

        self.__triangles = self.__program.triangle_list(TRIANGLES)

        self.__triangles.from_arrays(dict(
            position=positions,
            normal=normals))

    def __grid_n_cubes(self):
        """G.__grid_n_cubes() -> grid, cubes

        Loads the glass grid and cube coordinates from the file specified by
        the configuration.
        """

        filename = self.__config.grid_file()

        w, h, d = self.__config.grid_size()

        grid, cubes = numpy.zeros((w, h, d)), []

        for x, y, z, solid in grid_lines(filename):

            # Assuming solid is always either 1 or 0...
            if solid:

                cubes.append((x, y, z))

            grid[x, y, z] = solid

        # The sort ensures that the application of limits later on will not
        # depend upon the order in which the cubes were specified in the file.
        cubes.sort()
        cubes = numpy.array(cubes)

        return grid, cubes

    def on_draw(self):
        """G.on_draw()

        Renders the glass piece.
        """

        x_rep, y_rep, z_rep = self.__config.glass_repetitions()
        w, h, d = self.__config.grid_size()

        with self.__triangles as triangles:

            self.__camera.clear()
            self.__camera.add(*self.__cam.gl_matrix())
            self.__camera.set()

            if not self.__color.filled():
                self.__color.add(*self.__config.glass_color())
            self.__color.set()

            if not self.__sun.filled():
                self.__sun.add(*self.__config.sun_direction())
            self.__sun.set()

            for x_copy in range(x_rep):
                for y_copy in range(y_rep):
                    for z_copy in range(z_rep):

                        shift = (
                                w * x_copy,
                                h * y_copy,
                                d * z_copy)

                        self.__copy_shift.clear()
                        self.__copy_shift.add(*shift)
                        self.__copy_shift.set()

                        triangles.draw()
