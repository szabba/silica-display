# -*- coding: utf-8 -*-

__all__ = ['Config']

import os.path
import math
import argparse

import pyglet
from pyglet import gl

import numpy

from constants import *


def parse_args():
    """parse_args() -> the result of argparse's work"""

    parser = argparse.ArgumentParser()

    parser.add_argument(
            'GLASS_FILE',
            help='name of the glass file')

    parser.add_argument(
            '-s', '--slice',
            help=''.join([
                'slice of glass to display; described by enclosed cube ',
                'index ranges along all the axes']),
            nargs=6, type=int,
            default=(None, ) * 6)

    return parser.parse_args()


class Config(object):
    """The shared configuration of a display app."""

    def __init__(self):

        self.__args = parse_args()

        self.__sun = (gl.GLfloat * COORDINATES_PER_RAY)(
                *[0.5, 1, 1.5])

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

    def limits(self):
        """C.limits() -> x_min, x_max, y_min, y_max, z_min, z_max

        Limits of what part of the glass is visible. Integers or NoneS (for no
        limit).
        """

        return self.__args.slice

    def perspective_params(self):
        """C.perspective_params() -> (d0, d)"""

        return 50.0, 140.0

    def sun_direction(self):
        """C.sun_direction() -> a ctypes array of gl.GLfloats

        A vector describing the intensity and direction of the sunlight.
        """

        return self.__sun

    def init_scale(self):
        """C.init_scale() -> initial scaling factor"""

        return 10.0

    def init_phi(self):
        """C.init_phi() -> initial rotation about the z axis"""

        return 0.0

    def init_theta(self):
        """C.init_theta() -> initial rotation about the y axis"""

        return 0

    def init_translation(self):
        """C.init_translation() -> initial translation vector's coordinates"""

        return numpy.array([[0], [0], [0], [1]])

    def zoom_speed(self):
        """C.zoom_speed() -> zoom speed factor"""

        return 0.05

    def rot_z_speed(self):
        """C.rot_z_speed() -> speed of rotation about the z axis"""

        return 0.05

    def trans_speed(self):
        """C.translation_speed() -> speed of translation"""

        return 2.5

    def unit_factor(self):
        """C.unit_factor() -> factor fixing unit sizes"""

        return 5.

    def axis_ambient(self):
        """C.axis_ambient() -> gl.GLfloat"""

        return gl.GLfloat(0.4)

    def axis_diffuse(self):
        """C.axis_diffuse() -> gl.GLfloat"""

        return gl.GLfloat(0.6)
