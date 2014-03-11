# -*- coding: utf-8 -*-

import pyglet
from pyglet import gl

import shaders
from constants import *
from axes import Axes
from cam import Cam


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

    def sun_direction(self):
        """C.sun_direction() -> a ctypes array of gl.GLfloats

        A vector describing the intensity and direction of the sunlight.
        """

        return self.__sun

    def init_scale(self):
        """C.init_scale() -> initial scaling factor"""

        return 0.05

    def zoom_speed(self):
        """C.zoom_speed() -> zoom speed factor"""

        return 0.05

    def axis_ambient(self):
        """C.axis_ambient() -> gl.GLfloat"""

        return gl.GLfloat(0.4)

    def axis_diffuse(self):
        """C.axis_diffuse() -> gl.GLfloat"""

        return gl.GLfloat(0.6)


class Glass(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam


class Fog(object):
    """The glass (or it's visible part)"""

    def __init__(self, glass, cam):

        self.__glass = glass
        self.__cam = cam


class DisplayApp(object):
    """Main object"""

    def __init__(self, config):

        pyglet.window.Window.register_event_type('on_tick')

        self.__window = config.create_window()

        cam = Cam(config)

        glass = Glass(config, cam)

        self.__window.push_handlers(glass)

        self.__window.push_handlers(
                Particles(config, cam))

        self.__window.push_handlers(
                Fog(glass, cam))

        self.__window.push_handlers(
                Axes(config, cam))

        self.__window.push_handlers(
                cam)

        pyglet.clock.set_fps_limit(config.max_fps())

        self.__config = config

    def __tick(self, dt):
        """DA.__tick(dt)

        Dispatches an on_tick event to the underlying window. Gets called
        roughly each frame.
        """

        self.__window.dispatch_event('on_tick')

    def run(self):
        """DA.run()

        Runs the app.
        """

        if not gl.gl_info.have_version(3, 0):

            raise RuntimeError('OpenGL 3.0 required!')

        pyglet.clock.schedule_interval(
                self.__tick,
                1. / self.__config.max_fps())

        pyglet.app.run()


if __name__ == '__main__':

    app = DisplayApp(Config())
    app.run()
