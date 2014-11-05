# -*- coding: utf-8 -*-

__all__ = ['Fog']

from pyglet import gl

from silica.viz.common import shaders
from silica.viz.common import cube


class Fog(object):

    """Semi-transparent fog approximating ambient occlusion in the glass."""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__program = shaders.Program('fog')

        self.__camera = self.__program.uniform(
            'camera',
            shaders.GLSLType(shaders.GLSLType.Matrix(4)))

        self.__color = self.__program.uniform(
            'color',
            shaders.GLSLType(shaders.GLSLType.Vector(4)))

        self.__copy_shift = self.__program.uniform(
            'copy_shift',
            shaders.GLSLType(shaders.GLSLType.Vector(3)))

        self.__program.attribute(
            'position',
            shaders.GLSLType(shaders.GLSLType.Vector(3)))

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

    def __slice(self):
        """F.__slice() -> x_min, x_max, y_min, y_max, z_min, z_max"""

        W, H, D = self.__config.grid_size()
        x_min, x_max, y_min, y_max, z_min, z_max = self.__config.slice()

        x_min = 0 if x_min is None else x_min
        y_min = 0 if y_min is None else y_min
        z_min = 0 if z_min is None else z_min

        x_max = W - 1 if x_max is None else x_max
        y_max = H - 1 if y_max is None else y_max
        z_max = D - 1 if z_max is None else z_max

        return x_min, x_max, y_min, y_max, z_min, z_max

    def __fog_layer(self, i):
        """F.__fog_layer(i) -> TriangleList or None

        Returns the i-th layer TriangleList or None when one of the dimmesions
        would be 0.
        """

        x_min, x_max, y_min, y_max, z_min, z_max = self.__slice()

        w = x_max - x_min - 2 * i
        h = y_max - y_min - 2 * i
        d = z_max - z_min - 2 * i

        if w <= 0 or h <= 0 or d <= 0:
            return None

        x = x_min + i + 0.5
        y = y_min + i + 0.5
        z = z_min + i + 0.5

        positions = cube.CUBE_FACES.copy()

        positions[:, :, :, 0] *= w
        positions[:, :, :, 1] *= h
        positions[:, :, :, 2] *= d

        positions[:, :, :, 0] += x
        positions[:, :, :, 1] += y
        positions[:, :, :, 2] += z

        t_list = self.__program.triangle_list(
            cube.SQUARES_PER_CUBE *
            cube.TRIANGLES_PER_SQUARE)

        t_list.from_arrays(dict(position=positions))

        return t_list

    def on_draw(self):
        """F.on_draw()

        Renders the fog."""

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glDepthMask(gl.GL_FALSE)

        x_rep, y_rep, z_rep = self.__config.glass_repetitions()
        w, h, d = self.__config.grid_size()

        for layer in self.__layers:

            with layer:

                self.__camera.clear()
                self.__camera.add(*self.__cam.gl_matrix())
                self.__camera.set()

                if not self.__color.filled():
                    self.__color.add(*self.__config.fog_color())
                self.__color.set()

                for x_copy in range(x_rep):
                    for y_copy in range(y_rep):
                        for z_copy in range(z_rep):

                            shift = (
                                w * x_copy,
                                h * y_copy,
                                d * z_copy)

                            self.__copy_shift.clear()
                            self.__copy_shift.add(*shift)
                            self.__copy_shift.set()

                            layer.draw()

        gl.glDepthMask(gl.GL_TRUE)
        gl.glDisable(gl.GL_BLEND)
