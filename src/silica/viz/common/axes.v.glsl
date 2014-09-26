#version 120

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;
uniform mat4 camera = mat4(
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 0, 1);

attribute vec3 position;
attribute vec3 normal;
attribute vec3 color;

varying vec3 f_normal;
varying vec3 f_color;

void main(void) {

	gl_Position = camera * vec4(position, 1.0);

	f_normal = normal;

	f_color = color;
}
