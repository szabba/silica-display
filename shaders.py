# -*- coding: utf-8 -*-

__all__ = [
        'check_shader', 'check_program', 'load_shader', 'build_program',
        'Program', 'GLSLType']


import ctypes as c

from pyglet import gl


SHADER_TYPES = {
        'v': gl.GL_VERTEX_SHADER,
        'f': gl.GL_FRAGMENT_SHADER }


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

    # Generate the filename and read the contents
    filename = '%s.%s.glsl' % (name, shader_type)

    with open(filename) as source_file:
        source = source_file.read()

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


class GLSLType(object):
    """A GLSL type representation"""

    class Shape(object):
        """A shape of a GLSL value"""

        def to_api_string(self):

            raise NotImplementedError()

    class Scalar(Shape):

        def to_api_string(self):

            return "1"

    INT, FLOAT = range(2)

    @staticmethod
    def enshape(shape):
        """GLSLType.enshape(shape) -> shape

        Takes the given shape and returns it's "normal form".
        """

        if isinstance(shape, int):

            return (shape, 1)

        elif isinstance(shape, tuple) and len(shape) == 2:

            fst, snd = shape

            if fst == 1:

                return (snd, fst)

            return shape

        else:

            raise ValueError(
                    ("A GLSLType shape must be an integer or a two-integer" +
                        " tuple, not an %s") % type(shape))

    def __init__(self, element_type, shape=1):

        if element_type not in (GLSLType.INT, GLSLType.FLOAT):

            raise ValueError(
                    "A GLSLType element_type must be either GLSLType.INT" +\
                            " or GLSLType.FLOAT")

        shape = GLSLType.enshape(shape)

        if (shape not in [(1, 1), (2, 1), (3, 1), (4, 1)] and
                element_type == GLSLType.INT
                ):

            raise ValueError(
                "GLSL matrices cannot have integer elements in Opengl 2.1!")

        self.__elem_type = element_type
        self.__shape = shape


class Uniform(object):
    """A GLSL uniform value"""

    def __init__(self, program, uniform):

        self.__program = program
        self.__uniform = uniform


class Program(object):
    """A GLSL shader program"""

    def __init__(self, name):

        self.__program = build_program(name)

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

    def __exit__(self):

        self.unuse()
