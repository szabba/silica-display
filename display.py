# -*- coding: utf-8 -*-

import pyglet

from pyglet import gl


class Config(object):
    """The shared configuration of a display app."""

    __cls_init_done = False

    @classmethod
    def cls_init(cls):
        """Config.cls_init()

        Perform some one-time initialisation."""

        if not cls.__cls_init_done:

            pyglet.window.Window.register_event_type('on_tick')

            cls.__cls_init_done = True

    def __init__(self):

        self.__class__.cls_init()

    def create_window(self):
        """C.create_window()

        Create a new window, according to the specified config.
        """

        window = pyglet.window.Window(
                width=800,
                height=600,
                resizable=True)

        return window

    def max_fps(self):
        """C.max_fps()

        The maximum number of frames per second.
        """

        return 32


class Cam(object):
    """The camera"""

    def __init__(self, config):

        self.__config = config


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


class Axes(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam


class DisplayApp(object):
    """Main object"""

    def __init__(self, config):

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

    def __tick(self):
        """DA.__tick()

        Dispatches an on_tick event to the underlying window. Gets called
        roughly each frame.
        """

        self.__window.dispatch_event('on_tick')

    def run(self):
        """DA.run()

        Runs the app.
        """

        pyglet.clock.schedule_interval(
                self.__tick,
                1. / config.max_fps())

        pyglet.app.run()


if __name__ == '__main__':

    app = DisplayApp(Config())
    app.run()
