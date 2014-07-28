# -*- coding: utf-8 -*-

import math

import pyglet
from pyglet import gl

import shaders
import transform
from constants import *
from axes import Axes
from glass import Glass
from fog import Fog
from camera import Cameraman
from config import Config


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam


def common_transforms(transforms, config, window):
    """common_transforms(transforms, config, window)

    Stores the commnon transforms in a dictionary.
    """

    cam_geometry = transform.CameraGeometry(
            *config.perspective_params())

    foreshort = transform.Foreshortening(cam_geometry)

    transforms['aspect'] = aspect = transform.AspectRatio(*window.get_size())

    flip_hand = transform.FlipHandedness(Z_AXIS)

    project = transform.Product()
    project.add_factor(foreshort)
    project.add_factor(aspect)
    project.add_factor(flip_hand)

    transforms['scale'] = scale = transform.Scale(config.init_scale())

    transforms['look_at'] = look_at = transform.LookAt(
            cam_geometry, scale)

    transforms['rot_y'] = rot_y = transform.BasicAxisRotation(
            config.init_phi(), Y_AXIS)
    transforms['rot_z'] = rot_z = transform.BasicAxisRotation(
            config.init_theta(), Z_AXIS)
    rot_x = transform.BasicAxisRotation(-math.pi / 2, X_AXIS)

    transforms['rot'] = rot = transform.Product()
    rot.add_factor(rot_y)
    rot.add_factor(rot_z)
    rot.add_factor(rot_x)

    transforms['sr'] = sr = transform.Product()
    sr.add_factor(scale)
    sr.add_factor(rot)

    transforms['cam_shift'] = cam_shift = transform.Translate(
            *config.center_point())

    transforms['camera'] = camera = transform.Product()
    camera.add_factor(project)
    camera.add_factor(look_at)
    camera.add_factor(sr)
    camera.add_factor(cam_shift)

    return transforms


class DisplayApp(object):
    """Main object"""

    def __init__(self, config):

        pyglet.window.Window.register_event_type('on_tick')

        self.__window = config.create_window()
        keys = pyglet.window.key.KeyStateHandler()
        transforms = {}

        common_transforms(transforms, config, self.__window)

        cam = transforms['camera']

        self.__window.push_handlers(
                Axes(config, cam, self.__window))

        self.__window.push_handlers(
                Fog(config, cam))

        self.__window.push_handlers(
                Particles(config, cam))

        self.__window.push_handlers(
                Glass(config, cam))

        self.__window.push_handlers(
                Cameraman(config, keys, transforms))

        self.__window.push_handlers(
                keys)

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
