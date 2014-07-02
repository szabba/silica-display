# -*- coding: utf-8 -*-

import math

import pyglet
from pyglet import gl

import shaders
from constants import *
from axes import Axes
from glass import Glass
from fog import Fog
from camera import Camera
from config import Config


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam


class DisplayApp(object):
    """Main object"""

    def __init__(self, config):

        pyglet.window.Window.register_event_type('on_tick')

        self.__window = config.create_window()

        cam = Camera(config)

        self.__window.push_handlers(
                Particles(config, cam))

        self.__window.push_handlers(
                Fog(config, cam))

        self.__window.push_handlers(
                Glass(config, cam))

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

        if not gl.gl_info.have_version(2, 1):

            raise RuntimeError('OpenGL 2.1 required!')

        gl.glEnable(gl.GL_DEPTH_TEST)

        pyglet.clock.schedule_interval(
                self.__tick,
                1. / self.__config.max_fps())

        pyglet.app.run()


if __name__ == '__main__':

    app = DisplayApp(Config())
    app.run()
