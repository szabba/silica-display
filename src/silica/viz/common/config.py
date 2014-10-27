# -*- coding: utf-8 -*-

__all__ = ['BaseArgsParser', 'SlicedGridArgsParser', 'CommonConfig']

import argparse

import pyglet
from pyglet import gl
import numpy

from silica.viz.common.constants import COORDINATES_PER_RAY
from silica.viz.common import vector


class BaseArgsParser(argparse.ArgumentParser):
    """An argument parser accepting the common options to pyglet-based
    visualizations.
    """

    def __init__(self):

        super(BaseArgsParser, self).__init__()

        self.add_argument(
                '-F', '--fps', '--frame-rate',
                help='number of particle animation frames to play per second',
                type=float, default=3.0)


class SlicedGridArgsParser(BaseArgsParser):
    """An argument parser for things that display cubical grids that may be
    sliced.
    """

    def __init__(self):

        super(SlicedGridArgsParser, self).__init__()

        self.add_argument(
                '-s', '--slice',
                help=''.join([
                    'slice of ', self.object_sliced(), ' to display; described',
                    ' by enclosed cube index ranges along all the axes']),
                nargs=6, type=int,
                default=(None, ) * 6)

    def object_sliced(self):
        """SGAP.object_sliced() -> string

        Name of the object being sliced.
        """

        raise NotImplementedError(self.__class__.__name__, self.object_sliced.__name__)


class BaseConfig(object):
    """Basic configuration object"""

    def __init__(self, parsed_args):

        self._args = parsed_args

        self.__sun = (gl.GLfloat * COORDINATES_PER_RAY)(
                0.5, 1, 1.5)

    def create_window(self):
        """C.create_window() -> a window

        Create a new window, according to the specified config.
        """

        window = pyglet.window.Window(
                width=800,
                height=600,
                resizable=True)

        return window

    def max_fps(self):
        """C.max_fps() -> max fps

        The maximum number of frames per second.
        """

        return 32

    def center_point(self):
        """C.center_point() -> (x, y, z)

        Point at which the camea is initially looking.
        """

        return (0., 0., 0.)

    def perspective_params(self):
        """C.perspective_params() -> (d0, d)"""

        return 50.0, 14000.0

    def sun_direction(self):
        """C.sun_direction() -> a ctypes array of gl.GLfloats

        A vector describing the intensity and direction of the sunlight.
        """

        return self.__sun

    def init_scale(self):
        """C.init_scale() -> initial scaling factor"""

        return 1000.0

    def init_rot_basis(self):
        """C.init_rot_basis() -> inital rotated basis"""

        return vector.E_X, vector.E_Y, vector.E_Z

    def init_translation(self):
        """C.init_translation() -> initial translation vector's coordinates"""

        return numpy.array([[0], [0], [0], [1]], dtype=numpy.float)

    def zoom_speed(self):
        """C.zoom_speed() -> scale of scaling"""

        return 0.05

    def speed_along_sight_line(self):
        """C.speed_along_sight_line() -> speed of movement along the sight line"""

        return 3.0

    def rot_z_speed(self):
        """C.rot_z_speed() -> speed of rotation about the z axis"""

        return 0.005

    def trans_speed(self):
        """C.translation_speed() -> speed of translation"""

        return 120

    def unit_factor(self):
        """C.unit_factor() -> factor fixing unit sizes"""

        return 5.

    def axis_ambient(self):
        """C.axis_ambient() -> gl.GLfloat"""

        return gl.GLfloat(0.4)

    def axis_diffuse(self):
        """C.axis_diffuse() -> gl.GLfloat"""

        return gl.GLfloat(0.6)

    def axes_scale(self):
        """C.axes_scale() -> scaling factor for the axes"""

        return 8.

    def axes_size(self):
        """C.axes_size() -> width, height"""

        return 1., 8.

    def axes_position(self):
        """C.axis_position() -> the position of the central point of the helper
        axes

        Relative to the lower left corner of the window."""

        return 150., 150.


class SliceGridConfig(BaseConfig):
    """Config for apps containing sliceable grid-based objects"""

    def slice(self):
        """C.slice() -> (x_min, x_max, y_min, y_max, z_min, z_max)"""

        return self._args.slice
