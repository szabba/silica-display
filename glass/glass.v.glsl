#version 120

uniform mat4 camera;
uniform vec3 copy_shift;

attribute vec3 position;
attribute vec3 normal;

varying vec3 f_normal;
varying vec3 f_position;

void main(void) {

	gl_Position = camera * vec4(copy_shift + position, 1.0);

	f_normal = normal;
	f_position = position;
}
