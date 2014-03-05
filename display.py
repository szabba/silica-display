# -*- coding: utf-8 -*-

import pyglet

from pyglet import gl

import shaders


VERTICES_PER_TRIANGLE = 3
COORDINATES_PER_VERTEX = 3
COORDINATES_PER_NORMAL = 3
COORDINATES_PER_RAY = 3
RGB_COMPONENTS = 3
RGBA_COMPONENTS = 4


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

    def axis_ambient(self):
        """C.axis_ambient() -> gl.GLfloat"""

        return gl.GLfloat(0.4)

    def axis_diffuse(self):
        """C.axis_diffuse() -> gl.GLfloat"""

        return gl.GLfloat(0.6)


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

    AXIS_COUNT = 3
    TRIANGLES_PER_AXIS = 8

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.build_program('axes')

        self.__sun = self.__uniform_location('sun')
        self.__ambient = self.__uniform_location('ambient')
        self.__diffuse = self.__uniform_location('diffuse')
        self.__colors = self.__uniform_location('colors')

        self.__position = self.__attritbute_location('position')
        self.__normal = self.__attritbute_location('normal')
        self.__color_no = self.__attritbute_location('color_no')

        self.__axis_colors = (gl.GLfloat * (
            RGB_COMPONENTS * Axes.AXIS_COUNT))(
                    *[
                        1, 0, 0,
                        0, 1, 0,
                        0, 0, 1])


    def __uniform_location(self, name):
        """A.__uniform_location(name) -> location

        The OpenGL location of a uniform value.
        """

        return gl.glGetUniformLocation(
                self.__program, name)

    def __attritbute_location(self, name):
        """A.__attritbute_location(name) -> location

        The OpenGL location of an attribute.
        """

        return gl.glGetAttribLocation(
                self.__program, name)

    def on_draw(self):

        gl.glUseProgram(self.__program)

        gl.glUniform3fv(
                self.__sun, 1,
                self.__config.sun_direction())

        gl.glUniform1f(
                self.__ambient,
                self.__config.axis_ambient())

        gl.glUniform1f(
                self.__diffuse,
                self.__config.axis_diffuse())

        gl.glUniform3fv(
                self.__colors, 1,
                self.__axis_colors)

        gl.glUseProgram(0)


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
