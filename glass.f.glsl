#version 120

uniform vec3 color = vec3(1, 0, 0);
uniform vec3 sun;

varying vec3 f_normal;

void main(void) {

	gl_FragColor = vec4(color * dot(normalize(sun), f_normal), 1);
}
