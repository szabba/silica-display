# -*- coding: utf-8 -*-

__all__ = ['Camera']


import math

import numpy
from pyglet import gl
from pyglet import clock
from pyglet.window import mouse
from pyglet.window import key

import transform
from constants import X_AXIS, Y_AXIS, Z_AXIS


class Camera(transform.Transform):
    '''A camera'''

    def __init__(self, config, keys, window):

        super(Camera, self).__init__()

        self.__config = config
        self.__keys = keys

        clock.schedule(self.tick)

        self.__width, self.__height = window.get_size()

        self.__flip_hand = transform.FlipHandedness(Z_AXIS)
        self.__flip_hand.add_user(self)

        self.__sr = transform.Product()
        self.__sr.add_user(self)

        self.__scale = transform.Scale(config.init_scale())
        self.__sr.add_factor(self.__scale)

        self.__rot_y = transform.BasicAxisRotation(config.init_phi(), Y_AXIS)
        self.__sr.add_factor(self.__rot_y)

        self.__rot_z = transform.BasicAxisRotation(config.init_theta(), Z_AXIS)
        self.__sr.add_factor(self.__rot_z)

        self.__rot_x = transform.BasicAxisRotation(-math.pi / 2, X_AXIS)
        self.__sr.add_factor(self.__rot_x)

        self.__t = transform.Translate(*self.center_point())
        self.__t.add_user(self)

    def init_translation(self):
        """C.init_translation() -> numpy array

        Initial translation vector, in homogeneous coordinates, as a column matrix.
        """

        return numpy.array(
                self.center_point() + (1,),
                dtype=numpy.float
                ).reshape((4, 1))

    def center_point(self):
        """C.center_point() -> (x, y, z)

        Coordinates of the center of the repeated glass pieces.
        """

        dimmensions = self.__config.grid_size()
        repetitions = self.__config.glass_repetitions()

        return tuple(-(dim * rep) / 2.0 for dim, rep in zip(dimmensions, repetitions))

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

            self.__t.set_r(*self.center_point())
            self.__scale.set_scale(self.__config.init_scale())
            self.__rot_y.set_angle(self.__config.init_phi())
            self.__rot_z.set_angle(self.__config.init_theta())

            self.dirty()

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

            trans = numpy.array([self.__t.r()]).T

            trans += displacement * move.dot(k)[:3]

            r_x, r_y, r_z = trans[0, 0], trans[1, 0], trans[2, 0]

            self.__t.set_r(r_x, r_y, r_z)

    def foreshorten(self):
        """Camera.foreshorten() -> numpy array"""

        d0, d = self.__config.perspective_params()

        foreshort = numpy.array([
            [1., 0.,           0.,  0.],
            [0., 1.,           0.,  0.],
            [0., 0., 1./d0 + 2./d, -1.],
            [0., 0.,        1./d0,  1.]])

        return foreshort

    def aspect_ratio(self):
        '''C.aspect_ratio(width, height) -> numpy array'''

        aspect = numpy.eye(4)
        aspect[0, 0] = 2 / float(self.__width)
        aspect[1, 1] = 2 / float(self.__height)

        return aspect

    def look_at_middle(self):

        _, d = self.__config.perspective_params()
        s = self.__scale.scale()

        look_at = numpy.eye(4)

        look_at[2, 2] = 1 / s
        look_at[2, 3] = -d / 2

        return look_at

    def on_resize(self, width, height):

        self.__width = width
        self.__height = height

        self.dirty()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        scale = self.__scale.scale()

        if scroll_y < 0:
            scale *= (1 - self.__config.zoom_speed()) * abs(scroll_y)
        else:
            scale *= (1 + self.__config.zoom_speed()) * abs(scroll_y)

        self.__scale.set_scale(scale)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        if buttons == mouse.LEFT:

            phi = self.__rot_y.angle()
            phi += dx * self.__config.rot_z_speed()

            theta = self.__rot_z.angle()
            theta += dy * self.__config.rot_z_speed()

            self.__rot_y.set_angle(
                    limit_angle(
                        phi, (0, 2 * math.pi), WRAP))

            self.__rot_z.set_angle(
                    limit_angle(
                        theta, (-math.pi / 2, math.pi / 2), CUT_OFF))

        elif buttons == mouse.RIGHT:

            SR = self.__sr.matrix()

            u = numpy.array([[
                dx * self.__config.trans_speed(),
                dy * self.__config.trans_speed(),
                0, 0]]).T

            r = numpy.array([self.__t.r()]).T
            print 'r.shape', r.shape
            print 'inv(SR).shape', numpy.linalg.inv(SR).shape
            print 'u.shape', u.shape
            r += numpy.linalg.inv(SR).dot(u)[:3]

            self.__t.set_r(r[0, 0], r[1, 0], r[2, 0])

    def __dot(self, matrices, vect=numpy.array([[0], [0], [5], [1]])):

        matrix = numpy.eye(4)

        for other in reversed(matrices):

            matrix = other.dot(matrix)

        return matrix

    def calculate(self):

        self.set_matrix(self.__dot([
            self.foreshorten(),
            self.aspect_ratio(),
            self.__flip_hand.matrix(),
            self.look_at_middle(),
            self.__sr.matrix(),
            self.__t.matrix(),
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
