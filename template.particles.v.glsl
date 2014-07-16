#version 120

uniform mat4 camera;

uniform vec3[${vertex_count}] positions;
uniform vec3[${vertex_count}] normals;
uniform vec3[${vertex_count}] colours;

attribute float ix_float;
attribute vec3 position;
attribute vec2 orientation;

varying vec3 normal;
varying vec3 colour;

mat4 rotation_for(float rho, float theta) {

	return mat4(
			1, 0, 0, 0,
			0, 1, 0, 0,
			0, 0, 1, 0,
			0, 0, 0, 1);
}

void main(void) {

	int ix = int(ix_float);

	float rho = orientation.x;
	float theta = orientation.y;

	normal = normals[ix];
	colour = colours[ix];

	gl_Position = camera * rotation_for(rho, theta) * vec4(
			positions[ix] + position,
			1);
}
