#version 120

uniform vec3 color = vec3(1, 0, 0);
uniform vec3 sun;

uniform float ambient = 0.3;
uniform float diffuse = 0.7;

varying vec3 f_normal;

void main(void) {

	float diffuse_product = dot(normalize(sun), f_normal);
	diffuse_product *= - float(diffuse_product < 0);

	float intensity =
		ambient +
		diffuse * diffuse_product;

	gl_FragColor = vec4(color * intensity, 1);
}
