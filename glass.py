# -*- coding: utf-8 -*-

__all__ = ['Glass']


import os.path
import re

import numpy


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


class Glass(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

    def __load_grid(self):
        """G.__load_grid() -> numpy array of type int

        Loads the glass grid from a file specified by the configuration.
        """

        filename = self.__config.grid_file()

        w, h, d = guess_size(filename)

        grid = numpy.zeros((w, h, d), dtype=numpy.int)

        for x, y, z, solid in grid_lines(filename):

            grid[x, y, z] = solid

        return grid

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
