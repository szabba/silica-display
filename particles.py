# -*- coding: utf-8 -*-

__all__ = ['Particles']

import math
import string

import numpy
from pyglet.window import key

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


class AnimationBuilder(object):
    """A builder object for ParticleAnimations"""

    def __init__(self, program, model, particle_count):

        self.__program, self.__model = program, model

        self.__particle_count = particle_count
        self.__in_current_frame = 0
        self.__frames = []

        self.__start_frame()

    def __start_frame(self):
        """AB.__start_frame()

        Starts a new frame.
        """

        self.__in_current_frame = 0

        self.__frames.append({

            'ix_float': numpy.zeros((
                self.__particle_count,
                self.__model.vertex_count())),

            'position': numpy.zeros((
                self.__particle_count,
                self.__model.vertex_count(),
                COORDINATES_PER_VERTEX)),

            'orientation': numpy.zeros((
                self.__particle_count,
                self.__model.vertex_count(),
                ANGLES_PER_ORIENTATION)),
        })
        self.__frames[-1]['ix_float'][:] = numpy.arange(
                self.__model.vertex_count())

    @staticmethod
    def vector_to_angles(vector):
        """vector_to_angles((x, y, z)) -> rho, theta

        Calculates the angular representation of the direction the vector with
        the given components is pointing in.
        """

        x, y, z = vector

        phi = math.atan2(y, x)
        theta = math.atan2(z, math.sqrt(x**2 + y**2))

        return phi, theta

    def add_particle_state(self, position, orientation):
        """AB.add_particle_state(pos, dir)

        Both arguments are tuples. The first one is a particle's absolute space
        position. The second -- it's orientation as angles of rotation around
        the z and y axis.
        """

        if self.__in_current_frame == self.__particle_count:
            self.__start_frame()

        frame = self.__frames[-1]
        frame['position'][self.__in_current_frame, :] = position
        frame['orientation'][self.__in_current_frame, :] = orientation

        self.__in_current_frame += 1

    def build(self):
        """AB.build() -> ParticleAnimation"""

        t_lists = []
        for frame_data in self.__frames:

            t_list = self.__program.triangle_list(
                    self.__particle_count * self.__model.triangle_count())
            t_list.from_arrays(frame_data)

            t_lists.append(t_list)

        return ParticleAnimation(self.__particle_count, t_lists)


class ParticleAnimation(object):
    """A sequence of frames"""

    def __init__(self, particle_count, frames):

        self.__particle_count = particle_count
        self.__frames = frames

    @staticmethod
    def test_animation(program, model, particle_count, frame_count):
        """ParticleAnimation.test_animation(program, model, particle_count, frame_count) -> ParticleAnimation

        An example ParticleAnimation"""

        builder = AnimationBuilder(program, model, particle_count)

        for frame_no in range(frame_count):
            for particle_no in range(particle_count):

                builder.add_particle_state(
                        (6 * particle_no, 0, 0),
                        (2 * math.pi / frame_count * (particle_no + frame_no), 0))

        return builder.build()

    def __generate_frame(self, program, model, no):
        """PA.__generate_frame(program, model, no) -> triangle list

        No-th frame.
        """

        frame = program.triangle_list(
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
            particle[:, 0] = 2 * math.pi / self.frame_count() * (particle_no + no)

        frame.from_arrays(arrays)

        return frame

    def frame(self, no):
        """PA.frame(no) -> triangle list

        Data to render for the no-th current frame.
        """

        return self.__frames[no]

    def frame_count(self):
        """PA.frame_count() -> number of frames"""

        return len(self.__frames)

    def particle_count(self):
        """PA.particle_count() -> the number of particles being displayed"""

        return self.__particle_count


class ParticlePlayer(object):
    """Controls triangle list choice for the current frame."""

    def __init__(self, animation):

        self.__animation = animation
        self.__current_frame = 0

    def frame(self):
        """PP.frame() -> triangle list

        Data to render for the current frame.
        """

        return self.__animation.frame(self.__current_frame)

    def frame_count(self):
        """PP.frame_count() -> number of frames"""

        return self.__animation.frame_count()

    def particle_count(self):
        """PP.particle_count() -> the number of particles being displayed each frame"""

        return self.__animation.particle_count()

    def __first_frame(self):
        """PP.__first_frame() -> number of the first frame"""

        return 0

    def next_frame(self):
        """PP.next_frame()

        Move the animation forward in time by one frame.
        """

        self.__current_frame += 1

        if self.__current_frame >= self.frame_count():

            self.__current_frame = self.__first_frame()

    def previous_frame(self):
        """PP.previous_frame()

        Move the animation backward in time by one frame.
        """
        self.__current_frame -= 1

        if self.__current_frame < 0:

            self.__current_frame = self.__animation.frame_count() - 1


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

        animation = ParticleAnimation.test_animation(self.__program, self.__model, 4, 16)
        self.__player = ParticlePlayer(animation)

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

    def on_key_press(self, symbol, modifiers):

        if symbol == key.RIGHT:

            self.__player.next_frame()

        if symbol == key.LEFT:

            self.__player.previous_frame()

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
