# -*- coding: utf-8 -*-

__all__ = ['Cameraman', 'cam_transforms']


import math

import numpy
from pyglet import gl
from pyglet import clock
from pyglet.window import mouse
from pyglet.window import key

from silica.viz.common import transform
from silica.viz.common.constants import X_AXIS, Y_AXIS, Z_AXIS


def cam_transforms(transforms, config):
    """cam_transforms(transforms, config)

    Puts 'scale', 'sr', 'cam_shift' and 'camera' into the transform dict. These
    are the transforms and subtransforms expected by the Cameraman and not
    created by display.common_transforms.
    """

    cam_geometry = transform.CameraGeometry(
            *config.perspective_params())

    transforms['scale'] = scale = transform.Scale(config.init_scale())

    transforms['look_at'] = look_at = transform.LookAt(
            cam_geometry, scale)

    transforms['sr'] = sr = transform.Product()
    sr.add_factor(scale)
    sr.add_factor(transforms['rot'])

    transforms['cam_shift'] = cam_shift = transform.Translate(
            *config.center_point())

    transforms['camera'] = camera = transform.Product()
    camera.add_factor(transforms['project'])
    camera.add_factor(look_at)
    camera.add_factor(sr)
    camera.add_factor(cam_shift)


class Cameraman(object):
    '''Adjusts the camera parameters in reaction to external events.'''

    def __init__(self, config, keys, transforms):

        super(Cameraman, self).__init__()

        self.__config = config
        self.__keys = keys

        clock.schedule(self.tick)

        self.__aspect = transforms['aspect']
        self.__look_at = transforms['look_at']

        self.__sr = transforms['sr']
        self.__scale = transforms['scale']

        self.__rot = transforms['rot']

        self.__shift = transforms['cam_shift']

    def tick(self, dt):
        """C.tick(dt)

        Perform operations in need of being done at short time intervals.
        """

        self.move_along_sight_line(dt)
        self.center()

    def center(self):
        """C.center()

        Center the camera on the glass.
        """

        if self.__keys[key.C]:

            self.__shift.set_r(*self.__config.center_point())
            self.__scale.set_scale(self.__config.init_scale())
            self.__rot.set_basi(*config.init_rot_basis())

    def move_along_sight_line(self, dt):
        """C.move_along_sight_line(dt)

        Move the camera along the sight line if the UP or DOWN arrow key is
        pressed.
        """

        if self.__keys[key.UP] or self.__keys[key.DOWN]:

            speed = self.__scale.scale() * self.__config.speed_along_sight_line()

            displacement = speed * (
                    self.__keys.get(key.UP, 0) - self.__keys.get(key.DOWN, 0)
                    ) * dt

            k = numpy.array([[0, 0, 1, 1]]).T

            SR = self.__sr.matrix()

            move = numpy.linalg.inv(SR)

            trans = numpy.array([self.__shift.r()]).T

            trans += displacement * move.dot(k)[:3]

            r_x, r_y, r_z = trans[0, 0], trans[1, 0], trans[2, 0]

            self.__shift.set_r(r_x, r_y, r_z)

    def on_resize(self, width, height):

        self.__aspect.set_size(width, height)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        scale = self.__scale.scale()

        if scroll_y < 0:
            scale *= (1 - self.__config.zoom_speed()) * abs(scroll_y)
        else:
            scale *= (1 + self.__config.zoom_speed()) * abs(scroll_y)

        self.__scale.set_scale(scale)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        if buttons == mouse.LEFT:

            horiz, up, forward = self.__rot.basis()

            new_horiz = horiz.rotate(up, dx * self.__config.rot_z_speed())
            new_up = up.rotate(horiz, -dy * self.__config.rot_z_speed())
            new_forward = (forward.
                rotate(horiz, -dy * self.__config.rot_z_speed()).
                rotate(up, dx * self.__config.rot_z_speed()))

            self.__rot.set_basis(new_horiz, new_up, new_forward)


        elif buttons == mouse.RIGHT:

            SR = self.__sr.matrix()

            u = numpy.array([[
                dx * self.__config.trans_speed(),
                dy * self.__config.trans_speed(),
                0, 0]]).T

            r = numpy.array([self.__shift.r()]).T
            r += numpy.linalg.inv(SR).dot(u)[:3]

            self.__shift.set_r(r[0, 0], r[1, 0], r[2, 0])

    def __dot(self, matrices, vect=numpy.array([[0], [0], [5], [1]])):

        matrix = numpy.eye(4)

        for other in reversed(matrices):

            matrix = other.dot(matrix)

        return matrix

    def calculate(self):

        self.set_matrix(self.__dot([
            self.__foreshort.matrix(),
            self.__aspect.matrix(),
            self.__flip_hand.matrix(),
            self.__look_at.matrix(),
            self.__sr.matrix(),
            self.__shift.matrix(),
            ]))

    def on_draw(self):

        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)


CUT_OFF, WRAP = range(2)


def limit_angle(angle, interval, mode):
    """limit_angle(angle, (mini, maxi), mode) -> limited angle

    Ensures that the angle is between mini and maxi (inclusive). Mode is either
    CUT_OFF or WRAP.

    CUT_OFF means that the values outside of the interval are simply capped.

    WRAP means that adding n * (maxi - mini) to the angle (where n is an
    integer) won't affect the result.
    """

    mini, maxi = interval

    if mode is CUT_OFF:

        if angle < mini:
            angle = mini

        elif angle > maxi:
            angle = maxi

    elif mode is WRAP:

        period = maxi - mini

        while angle < mini:
            angle += period

        while angle >= maxi:
            angle -= period

    else:
        raise ValueError('mode must be either CUT_OFF or WRAP')

    return angle
