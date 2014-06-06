# -*- coding: utf-8 -*-

__all__ = ['Glass']

import os.path
import re

import numpy
from pyglet import gl

import shaders
from constants import *


TRIANGLES_PER_SQUARE = 2
SQUARES_PER_CUBE = 6


def guess_size(filename):
    """guess_size(filename) -> widht, height, depth

    Guess the size of a grid based on the name of the file that describes it.
    """

    match = re.match(
            r'data(?P<w>\d+)x(?P<h>\d+)x(?P<d>\d+)t\d+_\d+.dat',
            os.path.basename(filename))

    if match is None:
        raise ValueError(
                'Size of grid in \'%s\' cannot be guessed.' % filename)

    return (
            int(match.groupdict()['w']),
            int(match.groupdict()['h']),
            int(match.groupdict()['d']))


def grid_lines(filename):
    """grid_lines(filename) -> iter

    Returns an iterator ranging over the lines of a grid file.
    """

    with open(filename) as grid_file:
        for line in grid_file:

            yield tuple(map(int, line.split(' ')))


def cube_faces():
    """cube_faces() -> numpy array

    The coordinates of triangles forming a single cube.
    """

    faces = numpy.zeros((
        SQUARES_PER_CUBE,
        TRIANGLES_PER_SQUARE,
        VERTICES_PER_TRIANGLE,
        COORDINATES_PER_VERTEX))

    faces[0, 0] = [(0, 0, 0), (0, 1, 0), (0, 1, 1)]
    faces[0, 1] = [(0, 0, 0), (0, 1, 1), (0, 0, 1)]

    faces[1, 0] = [(0, 0, 0), (0, 0, 1), (1, 0, 1)]
    faces[1, 1] = [(0, 0, 0), (1, 0, 1), (1, 0, 0)]

    faces[2, 0] = [(0, 0, 0), (0, 1, 0), (1, 1, 0)]
    faces[2, 1] = [(0, 0, 0), (1, 1, 0), (1, 0, 0)]

    faces[3] = faces[0] + (1, 0, 0)
    faces[4] = faces[1] + (0, 1, 0)
    faces[5] = faces[2] + (0, 0, 1)

    return faces


def cube_normals():
    """cube_normals() -> numpy array

    The normals of a single cube.
    """

    normals = numpy.zeros((
        SQUARES_PER_CUBE,
        TRIANGLES_PER_SQUARE,
        VERTICES_PER_TRIANGLE,
        COORDINATES_PER_NORMAL))

    normals[0, :, :] = (-1, 0, 0)
    normals[1, :, :] = (0, -1, 0)
    normals[2, :, :] = (0, 0, -1)

    normals[3] -= normals[0]
    normals[4] -= normals[1]
    normals[5] -= normals[2]

    return normals


CUBE_FACES = cube_faces()
CUBE_NORMALS = cube_normals()


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

        self.__program.attribute(
                'position',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'normal',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        grid, cubes = self.__grid_n_cubes()

        self.__triangles = self.__program.triangle_list(
                reduce(lambda a, b: a * b, grid.shape) *
                SQUARES_PER_CUBE *
                TRIANGLES_PER_SQUARE)

        positions = self.__triangle_positions(grid)
        normals = self.__triangle_normals(grid)

        self.__triangles.from_arrays(dict(
            position=positions,
            normal=normals))

    def __grid_n_cubes(self):
        """G.__grid_n_cubes() -> grid, cubes

        Loads the glass grid and cube coordinates from the file specified by
        the configuration.
        """

        filename = self.__config.grid_file()

        w, h, d = guess_size(filename)

        grid, cubes = numpy.zeros((w, h, d)), []

        for x, y, z, solid in grid_lines(filename):

            # Assuming solid is always either 1 or 0...
            if solid:

                cubes.append((x, y, z))

            grid[x, y, z] = solid

        cubes = numpy.array(cubes)

        return grid, cubes

    def __limits(self, grid_shape):
        """G.__limits() -> x_min, x_max, y_min, y_max, z_min, z_max

        Limits -- all as integers. The grid shape is used to calculate the
        maximal values when values are None.
        """

        x_min, x_max, y_min, y_max, z_min, z_max = self.__config.limits()

        w, h, d = grid_shape

        x_min, y_min, z_min = max(x_min, 0), max(y_min, 0), max(z_min, 0)
        x_max = w if x_max is None else x_max
        y_max = h if y_max is None else y_max
        z_max = d if z_max is None else z_max

        return x_min, x_max, y_min, y_max, z_min, z_max

    def __only_visible(self, grid):
        """G.__only_visible(grid) -> grid'"""

        x_min, x_max, y_min, y_max, z_min, z_max = self.__limits(grid.shape)

        w, h, d = grid.shape

        mask = numpy.zeros(grid.shape, dtype=numpy.int)
        mask[:, :, :] = 1
        for i in range(w):
            for j in range(h):
                for k in range(d):

                    if (i < x_min or i > x_max or
                            j < y_min or j > y_max or
                            k < z_min or k > z_max):

                        mask[i, j, k] = 0

        return grid * mask

    def __overlaps_grid(self, visible):
        """G.__overlaps_grid(visible) -> overlaps grid

        Contains information about all the overlapping cube faces.

        The shape is (SQUARES_PER_CUBE, ) + grid.shape. The extra dimmension
        represent all six direction in which a cube's side can be facing.

        The value is 1 wherever the chosen side of the cube at specified
        coordinates is touching with the side of a neighbouring cube. All other
        values are 0.
        """

        W, H, D = visible.shape
        xyzs = numpy.mgrid[:W, :H, :D]

        overlaps = numpy.zeros((SQUARES_PER_CUBE, ) + visible.shape)

        for i in range(SQUARES_PER_CUBE / 2):

            safely_wrapped = numpy.roll(visible, -1, i) *
                (xyzs[i] == 0))

            overlaps[i] = visible != (
                numpy.roll(visible, -1, i) * (xyzs[i, :, :, :] == 0))

        for i in range(SQUARES_PER_CUBE / 2, SQUARES_PER_CUBE):

            safely_wrapped = numpy.roll(visible, 1, i % 3) *
                (xyzs[i % 3] == visible.shape[i % 3])

            overlaps[i] = visible != safely_wrapped

        return overlaps

    def __triangle_positions(self, grid):
        """G.__triangle_positions(grid) -> numpy array of triangle coordinates"""

        w, h, d = grid.shape

        print 'SQUARES: ', w * h * d * SQUARES_PER_CUBE

        triangs = numpy.zeros((
            w, h, d,
            SQUARES_PER_CUBE,
            TRIANGLES_PER_SQUARE,
            VERTICES_PER_TRIANGLE,
            COORDINATES_PER_VERTEX))

        triangs[:, :, :] = CUBE_FACES
        for i in range(w):
            for j in range(h):
                for k in range(d):
                    triangs[i, j, k] += (i, j, k)

        visible = self.__only_visible(grid)

        triangs[visible == 0] = 0

        return triangs

    def __triangle_normals(self, grid):
        """G.__triangle_normals(grid) -> numpy array of normals"""

        w, h, d = grid.shape

        normals = numpy.zeros((
            w, h, d,
            SQUARES_PER_CUBE,
            TRIANGLES_PER_SQUARE,
            VERTICES_PER_TRIANGLE,
            COORDINATES_PER_NORMAL))

        normals[:, :, :] = CUBE_NORMALS

        return normals

    def on_draw(self):
        """G.on_draw()

        Renders the glass piece."""

        with self.__triangles as triangles:

            self.__camera.clear()
            self.__camera.add(*self.__cam.gl_matrix())
            self.__camera.set()

            if not self.__sun.filled():
                self.__sun.add(*self.__config.sun_direction())
            self.__sun.set()

            triangles.draw()
