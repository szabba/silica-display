# -*- coding: utf-8 -*-

__all__ = ['GridCubeLoader', 'ArgsParser', 'Config', 'Potential']

import numpy
from pyglet import gl

from silica.viz.common.cube import TRIANGLES_PER_SQUARE
from silica.viz.common import shaders
from silica.viz.common.grid_surface import SurfaceDataGenerator
from silica.viz.common.config import CommonConfig, SlicedGridArgsParser


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


class ValueInRange(InclusionCondition):
    """Includes the grid cells with a values in a particular range"""

    def __init__(self, minimum, maximum):

        self.__min, self.__max = minimum, maximum

    def include(self, x, y, z, v):

        if self.__min is not None and v < self.__min:
            return False

        if self.__max is not None and self.__max < v:
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
        """GCL.load() -> numpy.ndarray"""

        self.__parse_size()
        for line in self.__input.readlines():
            self.__parse_value(line)

        self.__cubes = numpy.array(self.__cubes).reshape((-1, 3))

        return self.__grid, self.__cubes


class ArgsParser(SlicedGridArgsParser):
    """Argument parser for the potential visualization"""

    def __init__(self):

        super(ArgsParser, self).__init__()

        self.add_argument(
                'potential_file',
                help='file containing potential data to display')

    def object_sliced(self):
        "AP.object_sliced() -> name of object being sliced"""

        return 'potential'


class Config(CommonConfig):
    """Config for the potential visualization."""

    def potential_file(self):
        """C.potential_file() -> filename"""

        return self._args.potential_file

    def potential_min(self):
        """C.potential_min() -> minimal displayable potential value"""

        return None

    def potential_max(self):
        """C.potential_max() -> maximal displayable potential value"""

        return None

    def potential_color(self):
        """C.potential_color() -> (r, g, b)"""

        return (1., 1., 0.)

    def limits(self):
        """C.limits() -> (x_min, x_max, y_min, y_max, z_min, z_max)"""

        return self._args.slice


class Potential(object):
    """The potential surface"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.Program('potential')

        self.__camera = self.__program.uniform(
                'camera',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Matrix(4)))

        self.__sun = self.__program.uniform(
                'sun',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__color = self.__program.uniform(
                'color',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'position',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__program.attribute(
                'normal',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        includer = AndCondition(
                ValueInRange(
                    self.__config.potential_min(),
                    self.__config.potential_max()),
                Slice3D(*self.__config.limits()))

        with open(self.__config.potential_file()) as input_file:

            grid, cubes = GridCubeLoader(input_file, includer).load()

        surf_data_gen = SurfaceDataGenerator(grid, self.__config.limits())
        positions, normals = surf_data_gen.positions_and_normals(grid, cubes)

        SIDES = positions.shape[0]
        TRIANGLES = SIDES * TRIANGLES_PER_SQUARE

        self.__triangles = self.__program.triangle_list(TRIANGLES)

        self.__triangles.from_arrays(dict(
            position=positions,
            normal=normals))

    def on_draw(self):
        """P.on_draw()

        Renders the potential surface.
        """

        with self.__triangles as triangles:

            self.__camera.clear()
            self.__camera.add(*self.__cam.gl_matrix())
            self.__camera.set()

            if not self.__color.filled():
                self.__color.add(*self.__config.potential_color())
            self.__color.set()

            if not self.__sun.filled():
                self.__sun.add(*self.__config.sun_direction())
            self.__sun.set()

            triangles.draw()
