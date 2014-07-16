# -*- coding: utf-8 -*-

__all__ = ['Particles']

import numpy


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__model = self.__prepare_model()

    def __prepare_model(self):
        """P.__prepare_model() -> (poses, normals, colors, vertex_count)"""

        poses = numpy.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, -1, 0]])

        normals = numpy.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]])

        colors = numpy.array([
            [1, 0, 0],
            [0, 0, 1],
            [0, 0, 1]])

        vertex_count = 3

        return poses, normals, colors, vertex_count
