# -*- coding: utf-8 -*-

__all__ = ['Glass']

import os.path

import numpy
from scipy import weave
from pyglet import gl

from silica.viz.common import shaders
from silica.viz.common.constants import *
from silica.viz.common.cube import *


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


class SurfaceDataGenerator(object):
    """Generates surface data given a grid of cubes"""

    def __init__(self, grid, limits):

        self.__limits = limits
        self.__grid = grid

    def __only_visible(self, grid):
        """SDG.__only_visible(grid) -> grid'"""

        x_min, x_max, y_min, y_max, z_min, z_max = self.__limits

        w, h, d = grid.shape

        mask = numpy.zeros(grid.shape, dtype=numpy.int)
        mask[x_min:x_max+1, y_min:y_max+1, z_min:z_max+1] = 1

        return grid * mask

    def __overlaps_grid(self, visible):
        """SDG.__overlaps_grid(visible) -> overlaps grid

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
        """SDG.__nonoverlap_mask(grid, cubes) -> array

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

    def positions_and_normals(self, grid, cubes):
        """SDG.positions_and_normals(grid, cubes) -> vertices, normals

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

        return (
                raw_triangles[nonoverlap_mask.nonzero()],
                raw_normals[nonoverlap_mask.nonzero()])


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

        grid, cubes = self.__grid_n_cubes()
        surf_data_gen = SurfaceDataGenerator(grid, self.__config.limits())
        positions, normals = surf_data_gen.positions_and_normals(grid, cubes)

        SIDES = positions.shape[0]
        TRIANGLES = SIDES * TRIANGLES_PER_SQUARE

        self.__triangles = self.__program.triangle_list(TRIANGLES)

        self.__triangles.from_arrays(dict(
            position=positions,
            normal=normals))

    def __grid_n_cubes(self):
        """SDG.__grid_n_cubes() -> grid, cubes

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

        Renders the glass piece."""

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
