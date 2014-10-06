# -*- coding: utf-8 -*-

__all__ = [
        'GridCubeLoader', 'Sizer',
        'InclusionCondition', 'Slice3D', 'AndCondition']

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


class Sizer(object):
    """Determines the size of a cube grid"""

    def size(self):
        """S.size() -> (w, h, d)

        Dimmensions of the cube grid.
        """

        raise NotImplementedError(
                self.__class__.__name__,
                self.size.__name__)


class InclusionCondition(object):
    """Decides whether to ignore a given cell position"""

    def include(self, x, y, z, v):
        """IC.include(x, y, z, v) -> bool

        Should the grid cell at (x, y, z) with value v be included in what is
        displayed?
        """

        raise NotImplementedError(self.__class__.__name__, self.ignore.__name__)


class Slice3D(InclusionCondition):
    """An InclusionCondition that handles slicing of a shape consting of grid
    cells
    """

    def __init__(self, x_min, x_max, y_min, y_max, z_min, z_max):

        self.__x_min, self.__x_max = x_min, x_max
        self.__y_min, self.__y_max = y_min, y_max
        self.__z_min, self.__z_max = z_min, z_max

    def include(self, x, y, z, v):

        if self.__x_min is not None and x < self.__x_min:
            return False

        if self.__y_min is not None and y < self.__y_min:
            return False

        if self.__z_min is not None and z < self.__z_min:
            return False

        if self.__x_max is not None and self.__x_max < x:
            return False

        if self.__y_max is not None and self.__y_max < y:
            return False

        if self.__z_max is not None and self.__z_max < z:
            return False

        return True


class AndCondition(InclusionCondition):
    """Intersection of several InclusionConditions"""

    def __init__(self, *conds):

        self.__conds = conds

    def include(self, x, y, z, v):

        for cond in self.__conds:

            if not cond.include(x, y, z, v):
                return False

        return True
