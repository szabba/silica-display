#version 130

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;
uniform vec3[3] colors;
uniform mat4 camera = mat4(
		1, 0, 0, 0,
		0, 1, 0, 0,
		0, 0, 1, 0,
		0, 0, 0, 1);

attribute vec3 position;
attribute vec3 normal;
attribute int color_no;

varying vec3 local_normal;
varying vec3 color;

void main(void) {

	gl_Position = camera * vec4(position, 1.0);

	local_normal = normal;

	color = colors[color_no];
}
