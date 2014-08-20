# -*- coding: utf-8 -*-

__all__ = ['Particles']

import math
import string

import numpy

import shaders


class ParticleModel(object):
    """The 3D model for a single particle"""

    def __init__(self):

        self.__positions = numpy.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, -1, 0]])

        self.__normals = numpy.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]])

        self.__colours = numpy.array([
            [1, 0, 0],
            [0, 0, 1],
            [0, 0, 1]])

        self.__vertex_count = 3

    def generate_shader_source(self, template):
        """PM.generate_shader_source(template) -> shader source"""

        return template.substitute({
            'vertex_count': self.__vertex_count,
        })

    def vertex_count(self):
        """PM.vertex_count() -> number of triangle vertices in the model"""

        return self.__vertex_count

    def populate(self, positions, normals, colours):
        """PM.populate(position, normals, colours)

        Sets appropriate values for the model-dependant uniforms.
        """

        if not positions.filled():
            for position in self.__positions:
                positions.add(*position.flatten())
        positions.set()

        if not normals.filled():
            for normal in self.__normals:
                normals.add(*normal.flatten())
        normals.set()

        if not colours.filled():
            for colour in self.__colours:
                colours.add(*colour.flatten())
        colours.set()


class ParticlePlayer(object):
    """Controls triangle list choice for the current frame."""

    def __init__(self, program):

        self.__frame = program.triangle_list(1)
        self.__frame.from_arrays(dict(
            ix_float=[0, 1, 2],
            position=numpy.array([
                [10, 10, 10],
                [10, 10, 10],
                [10, 10, 10]]),
            orientation=numpy.array([
                [math.pi / 2, math.pi / 4],
                [math.pi / 2, math.pi / 4],
                [math.pi / 2, math.pi / 4]])))

    def frame(self):
        """PP.frame() -> triangle list

        Data to render for the current frame.
        """

        return self.__frame


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        self.__model = ParticleModel()

        self.__generate_shaders(self.__model)

        self.__program = shaders.Program('particles')

        self.__camera = self.__program.uniform(
                'camera',
                shaders.GLSLType(shaders.GLSLType.FLOAT, shaders.GLSLType.Matrix(4)))

        self.__sun = self.__program.uniform(
                'sun',
                shaders.GLSLType(shaders.GLSLType.FLOAT, shaders.GLSLType.Vector(3)))

        self.__positions = self.__program.uniform(
                'positions',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Vector(3)),
                self.__model.vertex_count())

        self.__normals = self.__program.uniform(
                'normals',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Vector(3)),
                self.__model.vertex_count())

        self.__colours = self.__program.uniform(
                'colours',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Vector(3)),
                self.__model.vertex_count())

        self.__ix = self.__program.attribute(
                'ix_float',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Scalar()))

        self.__position = self.__program.attribute(
                'position',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Vector(3)))

        self.__orientation = self.__program.attribute(
                'orientation',
                shaders.GLSLType(
                    shaders.GLSLType.FLOAT,
                    shaders.GLSLType.Vector(2)))

        self.__player = ParticlePlayer(self.__program)

    def __generate_shaders(self, model):
        """P.__generate_shaders(model)

        Generate tha shader sources.
        """

        for letter in ('v', 'f'):

            shader_filename = "particles.%s.glsl" % letter
            template_filename = "template.%s" % shader_filename

            with open(template_filename) as input:
                template = string.Template(input.read())

            shader_code = model.generate_shader_source(template)

            with open(shader_filename, 'w') as output:
                output.write(shader_code)

    def on_draw(self):
        """P.on_draw()

        Renders the particles.
        """

        with self.__player.frame() as frame:

            pass
