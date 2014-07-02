# -*- coding: utf-8 -*-

__all__ = [
        'CUBE_FACES', 'CUBE_NORMALS',
        'SQUARES_PER_CUBE', 'TRIANGLES_PER_SQUARE']

import numpy

from constants import *


TRIANGLES_PER_SQUARE = 2
SQUARES_PER_CUBE = 6


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

