# -*- coding: utf-8 -*-

__all__ = ['GridCubeLoader', 'Config', 'Potential']

import numpy

from silica.viz.common.config import CommonConfig


class GridCubeLoader(object):
    """Load a potential grid from a file-like object.

    The first line of the input should contain three numbers -- the dimmensions
    of the potential grid along the x, y, and z axis correspondingly.

    All following lines should contain four numbers each. The first three are
    coordinates of a point on the potential grid. The fourth is the value of
    the potential at that point.
    """

    def __init__(self, input_src, minimum, maximum):

        self.__input = input_src
        self.__min, self.__max = minimum, maximum

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

        if self.__min is not None and self.__min > value:
            return

        if self.__max is not None and self.__max < value:
            return

        self.__grid[x, y, z] = 1
        self.__cubes.append((x, y, z))

    def load(self):
        """GCL.load() -> numpy.ndarray"""

        self.__parse_size()
        for line in self.__input.readlines():
            self.__parse_value(line)

        self.__cubes = numpy.array(self.__cubes)

        return self.__grid, self.__cubes


class Config(CommonConfig):
    """Config for the potential visualization."""

    def potential_file(self):
        """C.potential_file() -> filename"""

        return 'garbage.potential'

    def potential_min(self):
        """C.potential_min() -> minimal displayable potential value"""

        return None

    def potential_max(self):
        """C.potential_max() -> maximal displayable potential value"""

        return None


class Potential(object):
    """The potential surface"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        with open(self.__config.potential_file()) as input_file:

            grid, cubes = GridCubeLoader(
                    input_file,
                    self.__config.potential_min(),
                    self.__config.potential_max()).load()

    def on_draw(self):
        """P.on_draw()

        Renders the potential surface.
        """
