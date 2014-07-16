# -*- coding: utf-8 -*-

__all__ = ['Particles']

import string

import numpy


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__model = self.__prepare_model()

        self.__generate_shaders(self.__model)

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

    def __generate_shaders(self, model):
        """P.__generate_shaders(model)

        Generate tha shader sources.
        """

        vertex_count = model[-1]

        data = {
                'vertex_count': vertex_count}

        for letter in ('v', 'f'):
            self.__generate_shader('particles', letter, data)

    def __generate_shader(self, shader_name, letter, data):
        """P.__generate_shader(self, shader_name, letter, data)

        Generate the appropriate shader source file.
        """

        shader_filename = "%s.%s.glsl" % (shader_name, letter)
        template_filename = "template.%s" % shader_filename

        with open(template_filename) as input:
            template = string.Template(input.read())

        shader_code = template.substitute(data)

        with open(shader_filename, 'w') as output:
            output.write(shader_code)
