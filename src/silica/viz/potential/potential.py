# -*- coding: utf-8 -*-

__all__ = ['GridCubeLoader', 'ArgsParser', 'Config', 'Potential']

import numpy
from pyglet import gl

from silica.viz.common.cube import TRIANGLES_PER_SQUARE
from silica.viz.common import shaders
from silica.viz.common.grid.surface import SurfaceDataGenerator
from silica.viz.common.grid.load import (
        GridCubeLoader, Sizer, InclusionCondition, AndCondition, Slice3D)
from silica.viz.common.config import SliceGridConfig, SlicedGridArgsParser


class Sizer(Sizer):
    """Sizer for a potential file"""

    def __init__(self, input_src):

        self.__input = input_src

    def size(self):

        line = self.__input.readline()
        w, h, d = map(int, map(float, line.split()))

        return w, h, d


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


class ArgsParser(SlicedGridArgsParser):
    """Argument parser for the potential visualization"""

    def __init__(self):

        super(ArgsParser, self).__init__()

        self.add_argument(
                '-m', '--min',
                help='minimal visible potential value',
               type=float, default=None)

        self.add_argument(
                '-M', '--max',
                help='minimal visible potential value',
                type=float, default=None)

        self.add_argument(
                'potential_file',
                help='file containing potential data to display')

    def object_sliced(self):
        "AP.object_sliced() -> name of object being sliced"""

        return 'potential'


class Config(SliceGridConfig):
    """Config for the potential visualization."""

    def potential_file(self):
        """C.potential_file() -> filename"""

        return self._args.potential_file

    def potential_min(self):
        """C.potential_min() -> minimal displayable potential value"""

        return self._args.min

    def potential_max(self):
        """C.potential_max() -> maximal displayable potential value"""

        return self._args.max

    def potential_color(self):
        """C.potential_color() -> (r, g, b)"""

        return (1., 1., 0.)


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
                Slice3D(*self.__config.slice()))

        with open(self.__config.potential_file()) as input_file:

            grid, cubes = GridCubeLoader(
                    input_file, includer, Sizer(input_file)).load()

        positions, normals = SurfaceDataGenerator(
                grid, cubes).positions_and_normals()

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
