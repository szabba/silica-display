#version 130

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;
uniform vec3[3] colors;

attribute vec3 position;
attribute vec3 normal;
attribute int color_no;

varying vec3 color;

vec3 unit(vec3 v) {

	return v / length(v);
}

void main(void) {

	gl_Position = vec4(position, 1.0);

	color = colors[color_no];
	color *= length(sun) * (ambient + dot(unit(sun), unit(normal)) * diffuse);
}
