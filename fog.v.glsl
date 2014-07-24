#version 120

uniform mat4 camera;
uniform vec3 copy_shift;

attribute vec3 position;

void main(void) {

	gl_Position = camera * vec4(copy_shift + position, 1.0);
}
