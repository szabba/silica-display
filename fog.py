# -*- coding: utf-8 -*-

__all__ = ['Fog']

from pyglet import gl

import shaders
import cube


class Fog(object):
    """Semi-transparent fog approximating ambient occlusion in the glass."""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.Program('fog')

        self.__camera = self.__program.uniform(
                'camera',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Matrix(4)))

        self.__color = self.__program.uniform(
                'color',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(4)))

        self.__program.attribute(
                'position',
                shaders.GLSLType(gl.GLfloat, shaders.GLSLType.Vector(3)))

        self.__layers = self.__fog_layers()

    def __fog_layers(self):
        """F.__fog_layers() -> list of TriangleListS

        They should all be drawn in order.
        """

        i, done, layers = 0, False, []

        while not done:

            last = self.__fog_layer(i)

            if last is None:
                done = True
            else:
                layers.append(last)

            i += 1

        layers.reverse()

        return layers

    def __fog_layer(self, i):
        """F.__fog_layer(i) -> TriangleList or None

        Returns the i-th layer TriangleList or None when one of the dimmesions
        would be 0.
        """

        x_min, x_max, y_min, y_max, z_min, z_max = self.__config.limits()

        w = x_max - x_min - i
        h = y_max - y_min - i
        d = z_max - z_min - i

        if w == 0 or h == 0 or d == 0:
            return None

        x = x_min + (i + 1) * 0.5
        y = y_min + (i + 1) * 0.5
        z = z_min + (i + 1) * 0.5

        positions = cube.CUBE_FACES.copy()

        positions[:, :, 0] *= w
        positions[:, :, 1] *= h
        positions[:, :, 2] *= d

        positions[:, :, 0] += x
        positions[:, :, 1] += y
        positions[:, :, 2] += z

        t_list = self.__program.triangle_list(
                cube.SQUARES_PER_CUBE *
                cube.TRIANGLES_PER_SQUARE)

        t_list.from_arrays(dict(position=positions))

        return t_list
