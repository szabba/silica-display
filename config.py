# -*- coding: utf-8 -*-

__all__ = ['Config']


import os.path
import sys
import re
import math
import argparse

import pyglet
from pyglet import gl

import numpy

from constants import *


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


def parse_args(args):
    """parse_args(args) -> the result of argparse's work"""

    parser = argparse.ArgumentParser()

    parser.add_argument(
            'GLASS_FILE',
            help='name of the glass file')

    parser.add_argument(
            '-p', '--particles',
            help='name of a file describing particle positions and orientations',
            default=None)

    parser.add_argument(
            '-s', '--slice',
            help=''.join([
                'slice of glass to display; described by enclosed cube ',
                'index ranges along all the axes']),
            nargs=6, type=int,
            default=(None, ) * 6)

    parser.add_argument(
            '-r', '--repeat',
            help=''.join('number of repetitions along each axis (x, y, z)'),
            nargs=3, type=int,
            default=(1, 1, 1))

    parser.add_argument(
            '-f', '--fog-color',
            help='RGBA color of the fog',
            nargs=4, type=float,
            default=(0, 1, 1, 0.125))

    parser.add_argument(
            '-g', '--glass-color',
            help='RGB color of the fog',
            nargs=3, type=float,
            default=(.7, .7, .7))

    return parser.parse_args(args)


class Config(object):
    """The shared configuration of a display app."""

    def __init__(self, args=sys.argv[1:]):

        self.__args = parse_args(args)

        self.__sun = (gl.GLfloat * COORDINATES_PER_RAY)(
                *[0.5, 1, 1.5])

        self.__grid_size = None

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

    def grid_file(self):
        """C.grid_file() -> filename

        Filename of the grid file.
        """

        return self.__args.GLASS_FILE

    def grid_size(self):
        """C.grid_size() -> (width, height, depth)

        Dimmensions of the glass grid, guessed from the filename.
        """

        if self.__grid_size is None:

            self.__grid_size = guess_size(self.grid_file())

        return self.__grid_size

    def glass_repetitions(self):
        """C.glass_repetitions() -> (x_rep, y_rep, z_rep)"""

        return self.__args.repeat

    def center_point(self):
        """C.center_point() -> (x, y, z)

        Coordinates of the center of the repeated glass pieces.
        """

        dimmensions = self.grid_size()
        repetitions = self.glass_repetitions()

        return tuple(-(dim * rep) / 2.0 for dim, rep in zip(dimmensions, repetitions))

    def glass_color(self):
        """C.glass_color() -> the RGB glass color"""

        return self.__args.glass_color

    def limits(self):
        """C.limits() -> x_min, x_max, y_min, y_max, z_min, z_max

        Limits of what part of the glass is visible. Integers or NoneS (for no
        limit).
        """

        w, h, d = self.grid_size()

        x_min, x_max, y_min, y_max, z_min, z_max = self.__args.slice

        if x_min is None:
            x_min = 0

        if y_min is None:
            y_min = 0

        if z_min is None:
            z_min = 0

        if x_max is None:
            x_max = w - 1

        if y_max is None:
            y_max = h - 1

        if z_max is None:
            z_max = d - 1

        return x_min, x_max, y_min, y_max, z_min, z_max

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

    def init_phi(self):
        """C.init_phi() -> initial rotation about the z axis"""

        return 0.0

    def init_theta(self):
        """C.init_theta() -> initial rotation about the y axis"""

        return 0

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

    def particle_dimmensions(self):
        """C.particle_dimmensions() -> height, width

        Dimmensions of the magnetic particles in glass grid units.
        """

        return 1, 0.5

    def fog_color(self):
        """C.fog_color() -> the RGBA fog color"""

        return self.__args.fog_color

    def particle_file(self):
        """C.particle_file() -> name of the particle file or None"""

        return None

    def particle_animation_fps(self):
        """C.particle_animation_fps() -> frame rate for particle animation"""

        return 3.0
