# -*- coding: utf-8 -*-

__all__ = ['Glass']

import os.path

import numpy
from scipy import weave
from pyglet import gl

import shaders
from constants import *
from cube import *


def grid_lines(filename):
    """grid_lines(filename) -> iter

    Returns an iterator ranging over the lines of a grid file.
    """

    with open(filename) as grid_file:
        for line in grid_file:

            yield tuple(map(int, line.split(' ')))


INLINE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'glass_inline.c')

with open(INLINE_PATH) as glass_inline_c:
    INLINE_CODE = glass_inline_c.read()


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
        positions, normals = self.__positions_and_normals(grid, cubes)

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
        # depend upon the order in which the cubes were specified in a file.
        cubes.sort()
        cubes = numpy.array(cubes)

        return grid, cubes

    def __only_visible(self, grid):
        """G.__only_visible(grid) -> grid'"""

        x_min, x_max, y_min, y_max, z_min, z_max = self.__config.limits()

        w, h, d = grid.shape

        mask = numpy.zeros(grid.shape, dtype=numpy.int)
        mask[x_min:x_max+1, y_min:y_max+1, z_min:z_max+1] = 1

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

        # Normals antiparallel to axes
        for i in range(SQUARES_PER_CUBE / 2):

            safely_wrapped = numpy.roll(visible, 1, i) *\
                (xyzs[i] == visible.shape[i])

            overlaps[i] = visible != safely_wrapped

        # Normals parallel to axes
        for i in range(SQUARES_PER_CUBE / 2, SQUARES_PER_CUBE):

            safely_wrapped = numpy.roll(visible, -1, i % 3) *\
                (xyzs[i % 3] == 0)

            overlaps[i] = visible != safely_wrapped

        return overlaps

    def __nonoverlap_mask(self, grid, cubes):
        """G.__nonoverlap_mask(grid, cubes) -> array

        A prefix-shaped mask for raw_triangles and raw_normals, to eliminate
        hidden triangles.
        """

        W, H, D = grid.shape
        CUBES = cubes.shape[0]

        visible = self.__only_visible(grid)
        overlaps_grid = self.__overlaps_grid(visible)

        nonoverlap_mask = numpy.zeros(
                (CUBES, SQUARES_PER_CUBE),
                dtype=numpy.int)

        weave.inline(
            INLINE_CODE,
            [
                'grid', 'visible', 'overlaps_grid',
                'nonoverlap_mask',
                'CUBES', 'SQUARES_PER_CUBE',
                'W', 'H', 'D',
            ],
            headers=[
                '<stdio.h>',
            ],
        )

        return nonoverlap_mask

    def __positions_and_normals(self, grid, cubes):
        """G.__positions_and_normals() -> vertices, normals

        Vertices and normals of visible triangles.
        """

        CUBES = cubes.shape[0]
        RAW_TRIANGLES_SIZE = RAW_NORMALS_SIZE = (
            CUBES, SQUARES_PER_CUBE,
            TRIANGLES_PER_SQUARE, VERTICES_PER_TRIANGLE,
            COORDINATES_PER_VERTEX,
        )

        # Normals at for possible cube side positions
        raw_normals = numpy.resize(
                CUBE_NORMALS,
                RAW_NORMALS_SIZE)

        # Coordinates for all possible triangles
        repeated_faces = CUBE_FACES[None].repeat(CUBES, 0)
        shifts_in_space = cubes[:, None, None, None, :].repeat(
                SQUARES_PER_CUBE, 1,
            ).repeat(
                TRIANGLES_PER_SQUARE, 2,
            ).repeat(
                VERTICES_PER_TRIANGLE, 3,
            )

        raw_triangles = repeated_faces + shifts_in_space

        # Normals and vertex positions for actually visible triangles
        nonoverlap_mask = self.__nonoverlap_mask(grid, cubes)

        print 'visible sides number:', nonoverlap_mask.sum()

        return (
                raw_triangles[nonoverlap_mask.nonzero()],
                raw_normals[nonoverlap_mask.nonzero()])

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
