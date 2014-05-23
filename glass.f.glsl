#version 120

uniform vec3 color = vec3(1, 0, 0);

void main(void) {

	gl_FragColor = vec4(color, 1);
}
