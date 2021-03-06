# -*- coding: utf-8 -*-

__all__ = [
    'check_shader', 'check_program', 'load_shader', 'build_program',
    'Program', 'GLSLType']


import os.path
import time
import ctypes as c

import numpy
from pyglet import gl

from silica.viz.common.constants import *


SHADER_TYPES = {
    'v': gl.GL_VERTEX_SHADER,
    'f': gl.GL_FRAGMENT_SHADER}


shader_path = []


def check_shader(shader, filename):
    """check_shader(shader, filename)

    Raises a RuntimeError if the shader hasn't compiled correctly."""

    # See if the shader compiled correctly
    compile_ok = gl.GLint(0)

    gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS,
                     c.pointer(compile_ok))

    # If the compilation fails, get the error description from OpenGL
    # and raise it
    if not compile_ok:
        log_len = gl.GLint(0)

        gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH,
                         c.pointer(log_len))

        log_buf = c.create_string_buffer(log_len.value)

        gl.glGetShaderInfoLog(shader, log_len, None, log_buf)

        raise RuntimeError(
            "Shader from %s could not compile: %s" % (
                filename, log_buf.value))


def check_program(program):
    """check_program(program)

    Raises a RuntimeError if the program hasn't linked correctly."""

    # See if the program linkd correctly
    link_ok = gl.GLint(0)

    gl.glGetProgramiv(program, gl.GL_LINK_STATUS,
                      c.pointer(link_ok))

    # If linking fails, get the error description from OpenGL and raise
    # it
    if not link_ok:
        log_len = gl.GLint(0)

        gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH,
                          c.pointer(log_len))

        log_buf = c.create_string_buffer(log_len.value)

        gl.glGetProgramInfoLog(program, log_len, None, log_buf)

        raise RuntimeError(
            "Program %d could not link: %s" % (
                program, log_buf.value))


def load_shader(name, shader_type):
    """load_shader(name, shader_type) -> compiled shader

    Exits the program if the shader doesn't compile."""

    # Check that the shader type specifier is correct
    if shader_type not in SHADER_TYPES:
        raise ValueError("%s is not a shader type specifier!" % shader_type)

    # Look for the shader file and when found -- read it's contents
    source, err = None, None
    for shader_dir in shader_path:
        filename = os.path.join(shader_dir, '%s.%s.glsl' % (name, shader_type))

        try:
            with open(filename) as source_file:
                source = source_file.read()
                break
        except IOError as io_err:
            err = io_err

    if source is None and err is not None:
        raise err

    # Perform ctypes enchantments
    source_buf = c.create_string_buffer(source)
    c_source = c.cast(source_buf,
                      c.POINTER(gl.GLchar))

    # Create and compile the shader
    shader = gl.glCreateShader(SHADER_TYPES[shader_type])

    gl.glShaderSource(shader, 1, c.pointer(c_source), None)
    gl.glCompileShader(shader)

    # If everything is ok -- return the shader
    check_shader(shader, filename)
    return shader


def build_program(name):
    """build_program(name)

    Loads and compiles the shaders and afterwards link them into a
    program."""

    # Compile the shaders
    vs = load_shader(name, 'v')

    fs = load_shader(name, 'f')

    # Create and link the program
    program = gl.glCreateProgram()

    gl.glAttachShader(program, vs)
    gl.glAttachShader(program, fs)

    gl.glLinkProgram(program)

    # If everything is ok -- return the program
    check_program(program)
    return program


def __max_vertex_attribute():
    """__max_vertex_attribute() -> int

    Maximal valid value for vertex attribute identifiers.
    """

    buffy = (1 * gl.GLint)()
    gl.glGetIntegerv(
        gl.GL_MAX_VERTEX_ATTRIBS,
        buffy)

    return buffy[0]


_MAX_VERTEX_ATTRIB = __max_vertex_attribute()


class GLSLType(object):

    """A GLSL type representation"""

    class Shape(object):

        """A shape of a GLSL value"""

        def to_api_string(self):

            raise NotImplementedError()

        def value_count(self):

            raise NotImplementedError()

    class Scalar(Shape):

        def to_api_string(self):

            return "1"

        def value_count(self):

            return 1

    class Vector(Shape):

        def __init__(self, size):

            self.__size = size

        def to_api_string(self):

            return str(self.__size)

        def value_count(self):

            return self.__size

    class Matrix(Shape):

        def __init__(self, size):

            self.__size = size

        def to_api_string(self):

            return "Matrix" + str(self.__size)

        def value_count(self):

            return self.__size * self.__size

    INT, FLOAT = gl.GLint, gl.GLfloat

    def __init__(self, shape=Scalar(), element_type=FLOAT):

        if (shape not in [(1, 1), (2, 1), (3, 1), (4, 1)] and
                element_type == GLSLType.INT):

            raise ValueError(
                "GLSL matrices cannot have integer elements in Opengl 2.1!")

        self.__elem_type = element_type
        self.__shape = shape

    def element_type(self):

        return self.__elem_type

    def element_type_tag(self):

        if self.element_type() is gl.GLint:

            return gl.GL_INT

        elif self.element_type() is gl.GLfloat:

            return gl.GL_FLOAT

    def uniform_setter(self):

        name = 'glUniform'

        name += self.__shape.to_api_string()

        name += 'i' if self.__elem_type == GLSLType.INT else 'f'

        name += 'v'

        setter = getattr(gl, name)

        if not isinstance(self.__shape, GLSLType.Matrix):

            return setter

        def better_setter(locus, count, data):

            setter(locus, count, gl.GL_TRUE, data)

        return better_setter

    def shape(self):

        return self.__shape


class Uniform(object):

    """A GLSL uniform value"""

    def __init__(self, program, uniform, type, count):

        self.__program = program
        self.__uniform = uniform
        self.__type = type
        self.__count = count

        element_type = self.__type.element_type()
        value_count = self.__type.shape().value_count()

        self.__buf = (element_type * (value_count * count))()
        self.__fill = 0

    def add(self, *values):

        if len(values) != self.__type.shape().value_count():

            raise TypeError(
                'This uniform requires %d components per value.' %
                self.__type.shape().value_count())

        for i, value in enumerate(values):

            self.__buf[self.__fill + i] = value

        self.__fill += len(values)

    def clear(self):

        self.__fill = 0

    def filled(self):

        return self.__fill == len(self.__buf)

    def set(self):

        setter = self.__type.uniform_setter()

        setter(self.__uniform, self.__count, self.__buf)


class Attribute(object):

    """A GLSL attribute"""

    def __init__(self, gl_id, gl_type, values_per_vertex):

        self.__gl_id = gl_id
        self.__gl_type = gl_type
        self.__values_per_vertex = values_per_vertex

    def components_per_vertex(self):
        """A.components_per_vertex() -> int

        The number of components that need to be specified each at each vertex.
        """

        components_per_value = self.__gl_type.shape().value_count()
        values_per_vertex = self.__values_per_vertex

        return components_per_value * values_per_vertex

    def c_array_for(self, triangle_count):
        """A.c_array_for(triangle_count) -> a ctypes array

        Creates a ctypes array with size and type appropriate for this
        attribute.
        """

        element_type = self.__gl_type.element_type()

        size = (triangle_count * VERTICES_PER_TRIANGLE *
                self.components_per_vertex())

        return (element_type * size)()

    def set(self, source):
        """A.set(source)

        Set the given attribute's value using the source for data.
        """

        if 0 <= self.__gl_id <= _MAX_VERTEX_ATTRIB:

            gl.glEnableVertexAttribArray(self.__gl_id)
            gl.glVertexAttribPointer(
                self.__gl_id,
                self.components_per_vertex(),
                self.__gl_type.element_type_tag(),
                gl.GL_FALSE, 0,
                source)

    def gl_type(self):
        """A.gl_type() -> GLSLType"""

        return self.__gl_type


class Program(object):

    """A GLSL shader program"""

    def __init__(self, name):

        self.__program = build_program(name)
        self.__uniforms = {}
        self.__attributes = {}

    def uniform(self, name, type, count=1):

        if name not in self.__uniforms:

            location = gl.glGetUniformLocation(
                self.__program, name)

            self.__uniforms[name] = Uniform(
                self.__program, location, type, count)

        return self.__uniforms[name]

    def attribute(self, name, type, values_per_vertex=1):

        if name not in self.__attributes:

            location = gl.glGetAttribLocation(
                self.__program, name)

            self.__attributes[name] = Attribute(
                location, type, values_per_vertex)

        return self.__attributes[name]

    def triangle_list(self, count):
        """P.triangle_list(count) -> a TriangleList

        Produces a triangle list that can be used to draw count triangles with
        the given shader program.
        """

        return TriangleList(self, count, self.__attributes)

    def use(self):
        """P.use()

        Enables the program for rendering.
        """

        gl.glUseProgram(self.__program)

    def unuse(self):
        """P.unuse()

        Disable the program for rendering.
        """

        gl.glUseProgram(0)

    def __enter__(self):

        self.use()
        return self

    def __exit__(self, type, value, traceback):

        self.unuse()


class TriangleList(object):

    """A set of data that can be used with a program to draw something."""

    def __init__(self, program, count, attrs):

        self.__program = program
        self.__count = count
        self.__attrs = attrs

        self.__arrays = {}
        for name, attr in self.__attrs.items():
            self.__arrays[name] = attr.c_array_for(self.__count)

    def from_arrays(self, arrays):
        """TL.from_arrays(arrays)

        Loads the data for all the attributes from an dictionary of ndarrays
        and other sequences containing the data. The arrays get implicitly
        flattened before use.
        """

        for name, array in self.__arrays.items():

            source = arrays[name]
            if isinstance(source, numpy.ndarray):
                source = source.flatten()

            for i in range(len(array)):
                array[i] = source[i]

    def __enter__(self):

        self.__program.use()

        for name, attr in self.__attrs.items():

            array = self.__arrays[name]

            attr.set(array)

        return self

    def draw(self):
        """TL.draw()

        Draws the triangle list on screen.
        """

        gl.glDrawArrays(
            gl.GL_TRIANGLES, 0,
            self.__count * VERTICES_PER_TRIANGLE)

    def __exit__(self, type, value, traceback):

        self.__program.unuse()
