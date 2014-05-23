#version 120

uniform mat4 camera;

attribute vec3 position;
attribute vec3 normal;

varying vec3 f_normal;

void main(void) {

	gl_Position = camera * vec4(position, 1.0);

	f_normal = normal;
}
