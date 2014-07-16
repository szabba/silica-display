#version 120

uniform mat4 camera;
uniform vec3 sun;

uniform float ambient = 0.3;
uniform float diffuse = 0.7;

varying vec3 normal;
varying vec3 colour;

void main(void) {

	vec3 act_normal = normalize(normal);

	float diffuse_product = dot(
			normalize(sun),
			normalize(normal));

	diffuse_product *= - float(diffuse_product < 0);

	float intensity = ambient + diffuse * diffuse_product;

	gl_FragColor = vec4(colour * intensity, 1);
}
