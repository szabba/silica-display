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

from silica.viz.common.constants import *
from silica.viz.common.config import SlicedGridArgsParser, CommonConfig


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


class ArgsParser(SlicedGridArgsParser):
    """Argument parser for the glass visualization."""

    def object_sliced(self):

        return 'glass'

    def __init__(self):

        super(ArgsParser, self).__init__()

        self.add_argument(
                '-g', '--glass-color',
                help='RGB color of the fog',
                nargs=3, type=float,
                default=(.7, .7, .7))

        self.add_argument(
                '-G', '--glass-file',
                help='name of the glass file',
                default=None)

        self.add_argument(
                '-p', '--particles',
                help='name of a file describing particle positions and orientations',
                default=None)

        self.add_argument(
                '-P', '--particle-dimmensions',
                help='length and width of a particle in glass grid units',
                nargs=2, type=float, default=(1, 0.5))

        self.add_argument(
                '-f', '--fog-color',
                help='RGBA color of the fog',
                nargs=4, type=float,
                default=(0, 1, 1, 0.125))

        self.add_argument(
                '-r', '--repeat',
                help=''.join('number of repetitions along each axis (x, y, z)'),
                nargs=3, type=int,
                default=(1, 1, 1))


class Config(CommonConfig):
    """The shared configuration of a display app."""

    def __init__(self, args=sys.argv[1:]):

        super(Config, self).__init__(
                ArgsParser().parse_args(args))

        self.__grid_size = None

    def grid_file(self):
        """C.grid_file() -> filename

        Filename of the grid file.
        """

        return self._args.glass_file

    def glass_specified(self):
        """C.glass_present() -> bool

        Was a glass file specified?
        """

        return self.grid_file() is not None

    def grid_size(self):
        """C.grid_size() -> (width, height, depth)

        Dimmensions of the glass grid, guessed from the filename.
        """

        if not self.glass_specified():

            return (0., 0., 0.)

        if self.__grid_size is None:

            self.__grid_size = guess_size(self.grid_file())

        return self.__grid_size

    def glass_repetitions(self):
        """C.glass_repetitions() -> (x_rep, y_rep, z_rep)"""

        return self._args.repeat

    def glass_color(self):
        """C.glass_color() -> the RGB glass color"""

        return self._args.glass_color

    def limits(self):
        """C.limits() -> x_min, x_max, y_min, y_max, z_min, z_max

        Limits of what part of the glass is visible. Integers or NoneS (for no
        limit).
        """

        w, h, d = self.grid_size()

        x_min, x_max, y_min, y_max, z_min, z_max = self._args.slice

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

    def particle_dimmensions(self):
        """C.particle_dimmensions() -> height, width

        Dimmensions of the magnetic particles in glass grid units.
        """

        return self._args.particle_dimmensions

    def fog_color(self):
        """C.fog_color() -> the RGBA fog color"""

        return self._args.fog_color

    def particle_file(self):
        """C.particle_file() -> name of the particle file or None"""

        return self._args.particles

    def particle_animation_fps(self):
        """C.particle_animation_fps() -> frame rate for particle animation"""

        return self._args.fps
