#version 130

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

varying vec3 local_normal;
varying vec3 local_color;

void main(void) {

	gl_Position = camera * vec4(position, 1.0);

	local_normal = normal;

	local_color = color;
}
