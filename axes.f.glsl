#version 120

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;

varying vec3 f_normal;
varying vec3 f_color;

void main(void) {

	vec3 act_normal = normalize(f_normal);

	float diffuse_product = dot(normalize(sun), act_normal);

	diffuse_product *= - float(diffuse_product < 0);

	float intensity =
		ambient +
		diffuse * diffuse_product;

	gl_FragColor = vec4(f_color * intensity, 1);
}
