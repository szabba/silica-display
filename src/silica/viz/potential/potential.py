# -*- coding: utf-8 -*-

__all__ = ['GridCubeLoader', 'ArgsParser', 'Config', 'Potential']

import numpy
from pyglet import gl

from silica.viz.common.cube import TRIANGLES_PER_SQUARE
from silica.viz.common import shaders
from silica.viz.common.grid_surface import SurfaceDataGenerator
from silica.viz.common.config import CommonConfig, SlicedGridArgsParser


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


class ArgsParser(SlicedGridArgsParser):
    """Argument parser for the potential visualization"""

    def object_sliced(self):
        "AP.object_sliced() -> name of object being sliced"""

        return 'potential'


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

    def potential_color(self):
        """C.potential_color() -> (r, g, b)"""

        return (1., 1., 0.)

    def limits(self):
        """C.limits() -> (x_min, x_max, y_min, y_max, z_min, z_max)"""

        return (0, 3, 0, 3, 0, 3)


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

        with open(self.__config.potential_file()) as input_file:

            grid, cubes = GridCubeLoader(
                    input_file,
                    self.__config.potential_min(),
                    self.__config.potential_max()).load()

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
