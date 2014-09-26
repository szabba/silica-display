# -*- coding: utf-8 -*-

import os.path
import math
import logging

import pyglet
from pyglet import gl

from silica.viz.common import shaders
from silica.viz.common import transform
from silica.viz.common.transform.dicts import common_transforms
from silica.viz.common.constants import *
from silica.viz.common.camera import Cameraman, cam_transforms
from silica.viz.common.axes import Axes
from silica.viz.glass.glass import Glass
from silica.viz.glass.fog import Fog
from silica.viz.glass.config import Config
from silica.viz.glass.particles import Particles


class DisplayApp(object):
    """Main object"""

    def __init__(self, config):

        self.__window = config.create_window()
        keys = pyglet.window.key.KeyStateHandler()
        transforms = {}

        common_transforms(transforms, config, self.__window)
        cam_transforms(transforms, config)

        cam = transforms['camera']

        self.__window.push_handlers(
                Axes(config, transforms, self.__window))

        self.__window.push_handlers(
                Fog(config, cam))

        if config.particle_file() is not None:

            if not os.path.exists(config.particle_file()):

                logging.error(
                        "Specified particle file '%s' does not exits",
                        config.particle_file())

            elif os.path.isdir(config.particle_file()):

                logging.error(
                        "Specified particles file '%s' is a directory",
                        config.particle_file())

            else:

                self.__window.push_handlers(
                        Particles(config, cam))

        if config.glass_specified():

            self.__window.push_handlers(
                    Glass(config, cam))

        self.__window.push_handlers(
                Cameraman(config, keys, transforms))

        self.__window.push_handlers(
                keys)

        pyglet.clock.set_fps_limit(config.max_fps())

        self.__config = config

    def run(self):
        """DA.run()

        Runs the app.
        """

        if not gl.gl_info.have_version(2, 1):

            raise RuntimeError('OpenGL 2.1 required!')

        gl.glEnable(gl.GL_DEPTH_TEST)

        pyglet.app.run()


if __name__ == '__main__':

    shaders.shader_path.append(os.path.dirname(__file__))

    app = DisplayApp(Config())
    app.run()
