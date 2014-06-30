#version 120

uniform mat4 camera;

attribute vec3 position;

void main(void) {

	gl_Position = camera * vec4(position, 1.0);
}
