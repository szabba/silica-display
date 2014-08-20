# -*- coding: utf-8 -*-

__all__ = ['Particles']

import math
import string

import numpy

import cube
import shaders
from constants import *


ANGLES_PER_ORIENTATION = 2


class ParticleModel(object):
    """The 3D model for a single particle"""

    def __init__(self, height, width):

        SHAPE = (2, ) + cube.CUBE_FACES.shape

        self.__positions = numpy.zeros(SHAPE)
        self.__positions[:] = cube.CUBE_FACES

        self.__positions[..., 0] *= height / 2.
        self.__positions[0, ..., 0] -= height / 2.
        self.__positions[..., 1:] *= width
        self.__positions[..., 1:] -= width / 2.

        self.__normals = numpy.zeros(SHAPE)
        self.__normals[:] = cube.CUBE_NORMALS

        self.__colours = numpy.zeros(SHAPE)
        self.__colours[0, ..., 0] = 1
        self.__colours[1, ..., 2] = 1

        self.__positions = self.__positions.reshape((-1, COORDINATES_PER_VERTEX))
        self.__normals = self.__normals.reshape((-1, COORDINATES_PER_VERTEX))
        self.__colours = self.__colours.reshape((-1, COORDINATES_PER_VERTEX))

        self.__vertex_count = self.__positions.size / COORDINATES_PER_VERTEX

    def generate_shader_source(self, template):
        """PM.generate_shader_source(template) -> shader source"""

        return template.substitute({
            'vertex_count': self.__vertex_count,
        })

    def vertex_count(self):
        """PM.vertex_count() -> number of triangle vertices in the model"""

        return self.__vertex_count

    def triangle_count(self):
        """PM.triangle_count() -> number of triangles in the model"""

        return self.vertex_count() / VERTICES_PER_TRIANGLE

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

    def __init__(self, program, model):

        self.__frame = program.triangle_list(
                self.particle_count() * model.triangle_count())
        arrays = {}

        arrays['ix_float'] = numpy.zeros((
            self.particle_count(),
            model.vertex_count()))
        arrays['ix_float'][:] = numpy.arange(model.vertex_count())

        arrays['position'] = numpy.zeros((
            self.particle_count(),
            model.vertex_count(),
            COORDINATES_PER_VERTEX))

        for particle_no, particle in enumerate(arrays['position']):
            particle[:, 0] += 6 * particle_no

        arrays['orientation'] = numpy.zeros((
            self.particle_count(),
            model.vertex_count(),
            ANGLES_PER_ORIENTATION))

        for particle_no, particle in enumerate(arrays['orientation']):
            particle[:, 0] = math.pi / 7 * particle_no

        self.__frame.from_arrays(arrays)

    def frame(self):
        """PP.frame() -> triangle list

        Data to render for the current frame.
        """

        return self.__frame

    def particle_count(self):
        """PP.particle_count() -> the number of particles being displayed"""

        return 4


class Particles(object):
    """The glass (or it's visible part)"""

    def __init__(self, config, cam):

        self.__config = config
        self.__cam = cam

        height, width = config.particle_dimmensions()
        self.__model = ParticleModel(height, width)

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

        self.__player = ParticlePlayer(self.__program, self.__model)

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

            self.__camera.clear()
            self.__camera.add(*self.__cam.gl_matrix())
            self.__camera.set()

            if not self.__sun.filled():
                self.__sun.add(*self.__config.sun_direction())
            self.__sun.set()

            self.__model.populate(
                    self.__positions,
                    self.__normals,
                    self.__colours)

            frame.draw()
