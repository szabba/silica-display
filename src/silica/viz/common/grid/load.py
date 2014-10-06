# -*- coding: utf-8 -*-

__all__ = ['GridCubeLoader']

import numpy


class GridCubeLoader(object):
    """Load a potential grid from a file-like object.

    The first line of the input should contain three numbers -- the dimmensions
    of the potential grid along the x, y, and z axis correspondingly.

    All following lines should contain four numbers each. The first three are
    coordinates of a point on the potential grid. The fourth is the value of
    the potential at that point.
    """

    def __init__(self, input_src, condition):

        self.__input = input_src
        self.__condition = condition

        self.__grid = None
        self.__cubes = []

    def __parse_size(self):
        """GCL.__parse_size()

        Parse the first line of a potential file, specifying the potential grid size.
        """

        line = self.__input.readline()
        w, h, d = line.split()

        grid_size = (int(float(w)), int(float(h)), int(float(d)))

        self.__grid = numpy.zeros(grid_size)

    def __parse_value(self, line):
        """GCL.__parse_value(line)

        Parse a line specifying a potential value at a certain grid position.
        """

        x, y, z, value = line.split()

        x, y, z = int(float(x)), int(float(y)), int(float(z))
        value = float(value)

        if self.__condition.include(x, y, z, value):

            self.__grid[x, y, z] = 1
            self.__cubes.append((x, y, z))

    def load(self):
        """GCL.load() -> grid array, cube position array"""

        self.__parse_size()
        for line in self.__input.readlines():
            self.__parse_value(line)

        self.__cubes = numpy.array(self.__cubes).reshape((-1, 3))

        return self.__grid, self.__cubes
