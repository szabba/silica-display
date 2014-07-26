# -*- coding: utf-8 -*-

__all__ = ['Camera']


import math

import numpy
from pyglet import gl
from pyglet import clock
from pyglet.window import mouse
from pyglet.window import key


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


class Camera(object):
    '''A camera'''

    def __init__(self, config, keys):

        self.__config = config
        self.__keys = keys

        clock.schedule(self.tick)

        self.__width, self.__height = 1, 1

        self.__scale = config.init_scale()

        self.__phi = config.init_phi()
        self.__theta = config.init_theta()

        self.__trans = self.init_translation()

        self.__matrix = None
        self.__gl_matrix = None

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

            self.__trans = self.init_translation()
            self.__scale = self.__config.init_scale()
            self.__phi = self.__config.init_phi()
            self.__theta = self.__config.init_theta()

            self.dirty()

    def move_along_sight_line(self, dt):
        """C.move_along_sight_line(dt)

        Move the camera along the sight line if the UP or DOWN arrow key is
        pressed.
        """

        if self.__keys[key.UP] or self.__keys[key.DOWN]:

            speed = self.__scale * self.__config.speed_along_sight_line()

            displacement = speed * (
                    self.__keys.get(key.UP, 0) - self.__keys.get(key.DOWN, 0)
                    ) * dt

            k = numpy.array([[0, 0, 1, 1]]).T

            SR = self.sr_matrix()

            move = numpy.linalg.inv(SR)

            self.__trans[:3] = self.__trans[:3] + displacement * move.dot(k)[:3]

            self.dirty()

    def foreshorten(self):
        """Camera.foreshorten() -> numpy array"""

        d0, d = self.__config.perspective_params()

        foreshort = numpy.array([
            [1., 0.,           0.,  0.],
            [0., 1.,           0.,  0.],
            [0., 0., 1./d0 + 2./d, -1.],
            [0., 0.,        1./d0,  1.]])

        print "foreshort"
        print foreshort
        print

        return foreshort

    def aspect_ratio(self):
        '''C.aspect_ratio(width, height) -> numpy array'''

        aspect = numpy.eye(4)
        aspect[0, 0] = 2 / float(self.__width)
        aspect[1, 1] = 2 / float(self.__height)

        print "aspect"
        print aspect
        print

        return aspect

    @staticmethod
    def flip_handedness():
        '''Camera.flip_handedness() -> numpy array'''

        fliper = numpy.eye(4)
        fliper[2, 2] = -1

        print "fliper"
        print fliper
        print

        return fliper

    def look_at_middle(self):

        _, d = self.__config.perspective_params()
        s = self.__scale

        look_at = numpy.eye(4)

        look_at[2, 2] = 1 / s
        look_at[2, 3] = -d / 2

        print "look_at"
        print look_at
        print

        return look_at

    def scale(self):

        scale = numpy.eye(4)

        scale[:3, :3] *= self.__scale

        print "scale"
        print scale
        print

        return scale

    def rot_z(self):

        cos = math.cos(self.__phi)
        sin = math.sin(self.__phi)

        rot_z = numpy.array([
            [cos, -sin, 0, 0],
            [sin,  cos, 0, 0],
            [  0,    0, 1, 0],
            [  0,    0, 0, 1]])

        print "rot_z"
        print rot_z
        print

        return rot_z

    def rot_y(self):

        cos = math.cos(self.__theta)
        sin = math.sin(self.__theta)

        rot_y = numpy.array([
            [cos, 0, -sin, 0],
            [  0, 1,    0, 0],
            [sin, 0,  cos, 0],
            [  0, 0,    0, 1]])

        print "rot_y"
        print rot_y
        print

        return rot_y

    def rot_x(self):

        angle = -math.pi / 2

        cos = math.cos(angle)
        sin = math.sin(angle)

        rot_x = numpy.array([
            [1,   0,    0, 0],
            [0, cos, -sin, 0],
            [0, sin,  cos, 0],
            [0,   0,    0, 1]])

        print "rot_x"
        print rot_x
        print

        return rot_x

    def translate(self):

        translate = numpy.eye(4)

        translate[:, 3] = self.__trans.reshape((4,))

        print "translate"
        print translate
        print

        return translate

    def dirty(self):
        '''C.dirty()

        Forces the matrices to be recalculated the next time they are requested.
        '''

        self.__matrix = None
        self.__sr_matrix = None
        self.__gl_matrix = None

    def on_resize(self, width, height):

        self.__width = width
        self.__height = height

        self.dirty()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):

        if scroll_y < 0:
            self.__scale *= (1 - self.__config.zoom_speed()) * abs(scroll_y)
        else:
            self.__scale *= (1 + self.__config.zoom_speed()) * abs(scroll_y)

        self.dirty()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):

        if buttons == mouse.LEFT:

            self.__phi += dy * self.__config.rot_z_speed()

            self.__theta += dx * self.__config.rot_z_speed()

            self.__phi = limit_angle(self.__phi, (-math.pi / 2, math.pi / 2), CUT_OFF)
            self.__theta = limit_angle(self.__theta, (0, 2 * math.pi), WRAP)

        elif buttons == mouse.RIGHT:

            SR = self.sr_matrix()

            u = numpy.array([
                [dx * self.__config.trans_speed()],
                [dy * self.__config.trans_speed()],
                [0],
                [0]])

            self.__trans = self.__trans + numpy.linalg.inv(SR).dot(u)

        self.dirty()

    def __dot(self, matrices, vect=numpy.array([[0], [0], [5], [1]])):

        matrix = numpy.eye(4)

        for other in reversed(matrices):

            matrix = other.dot(matrix)

        return matrix

    def sr_matrix(self):
        """C.sr_matrix() -> transform matrix

        A matrix that performs the same rotation and scaling as the camera.
        Useful in converting window coordinates to object coordinates.
        """

        if self.__sr_matrix is None:

            self.__sr_matrix = self.__dot([
                    self.scale(),
                    self.rot_y(),
                    self.rot_z(),
                    self.rot_x(),
                    ])

        return self.__sr_matrix

    def matrix(self):
        """C.matrix() -> camera matrix"""

        if self.__matrix is None:

            self.__matrix = self.__dot([
                    self.foreshorten(),
                    self.aspect_ratio(),
                    Camera.flip_handedness(),
                    self.look_at_middle(),
                    self.sr_matrix(),
                    self.translate(),
                    ])

        print self.__matrix
        print

        return self.__matrix

    def gl_matrix(self):
        """C.gl_matrix() -> OpenGL camera matrix as ctypes array"""

        if self.__gl_matrix is None:

            self.__gl_matrix = (gl.GLfloat * 16)()

            for i, elem in enumerate(self.matrix().flat):

                self.__gl_matrix[i] = elem

        return self.__gl_matrix

    def on_draw(self):

        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

