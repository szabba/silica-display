# -*- coding: utf-8 -*-

__all__ = ['Fog']

from pyglet import gl

import shaders


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

    def __fog_layers(self):
        """F.__fog_layers() -> list of TriangleListS

        They should all be drawn in order."""

        return []
	 
    def __fog_layer(self, i):
        """F.__fog_layer(i) -> TriangleList or None

        Returns the i-th layer TriangleList or None when one of the dimmesions
        would be 0.
        """

        return None
