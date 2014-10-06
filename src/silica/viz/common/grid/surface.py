# -*- coding: utf-8 -*-

__all__ = ['SurfaceDataGenerator']

import os.path

import numpy
from scipy import weave

from silica.viz.common.constants import *
from silica.viz.common.cube import *


INLINE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'surface_inline.c')

with open(INLINE_PATH) as glass_inline_c:
    INLINE_CODE = glass_inline_c.read()


class SurfaceDataGenerator(object):
    """Generates surface data given a grid of cubes"""

    def __init__(self, grid):

        self.__grid = grid

    def __overlaps_grid(self, grid):
        """SDG.__overlaps_grid(grid) -> overlaps grid

        Contains information about all the overlapping cube faces.

        The shape is (SQUARES_PER_CUBE, ) + grid.shape. The extra dimmension
        represent all six direction in which a cube's side can be facing.

        The value is 1 wherever the chosen side of the cube at specified
        coordinates is touching with the side of a neighbouring cube. All other
        values are 0.
        """

        W, H, D = grid.shape
        xyzs = numpy.mgrid[:W, :H, :D]

        overlaps = numpy.zeros((SQUARES_PER_CUBE, ) + grid.shape)

        # Normals antiparallel to axes
        for i in range(SQUARES_PER_CUBE / 2):

            safely_wrapped = numpy.roll(grid, 1, i) *\
                (xyzs[i] == grid.shape[i])

            overlaps[i] = grid != safely_wrapped

        # Normals parallel to axes
        for i in range(SQUARES_PER_CUBE / 2, SQUARES_PER_CUBE):

            safely_wrapped = numpy.roll(grid, -1, i % 3) *\
                (xyzs[i % 3] == 0)

            overlaps[i] = grid != safely_wrapped

        return overlaps

    def __nonoverlap_mask(self, grid, cubes):
        """SDG.__nonoverlap_mask(grid, cubes) -> array

        A prefix-shaped mask for raw_triangles and raw_normals, to eliminate
        hidden triangles.
        """

        W, H, D = grid.shape
        CUBES = cubes.shape[0]

        overlaps_grid = self.__overlaps_grid(grid)

        nonoverlap_mask = numpy.zeros(
                (CUBES, SQUARES_PER_CUBE),
                dtype=numpy.int)

        weave.inline(
            INLINE_CODE,
            [
                'grid', 'overlaps_grid', 'nonoverlap_mask',
                'CUBES', 'SQUARES_PER_CUBE', 'W', 'H', 'D',
            ],
            headers=[
                '<stdio.h>',
            ],
        )

        return nonoverlap_mask

    def no_cubes(self, shape):
        """SDG.no_cubes(shape) -> vertices, normals

        Vertex and normal values to use when there are no cubes to show.
        """

        return numpy.zeros(shape), numpy.zeros(shape)

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

        # FIXME: It shouldn't be necessary to special-case this
        if not CUBES:
            return self.no_cubes(RAW_TRIANGLES_SIZE)

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
