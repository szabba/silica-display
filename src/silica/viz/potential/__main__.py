# -*- coding: utf-8 -*-

import os.path
import sys
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
from silica.viz.common.config import BaseArgsParser
from silica.viz.potential.potential import Config, Potential


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
                Potential(config, cam))

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

    args = BaseArgsParser().parse_args(sys.argv[1:])
    config = Config(args)
    DisplayApp(config).run()
