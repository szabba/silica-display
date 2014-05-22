# -*- coding: utf-8 -*-

__all__ = ['Config']

import os.path
import math

import pyglet
from pyglet import gl

import numpy

from constants import *


class Config(object):
    """The shared configuration of a display app."""

    def __init__(self):

        self.__sun = (gl.GLfloat * COORDINATES_PER_RAY)(
                *[1, 1, 1])

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

        return os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__name__))),
                'SYM0',
                'data50x50x50t9000_102870.dat')

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
