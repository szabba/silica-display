#version 130

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;

varying vec3 local_normal;
varying vec3 color;

void main(void) {

	float I_0 = length(sun);

	vec3 sun_dir = normalize(sun);
	vec3 normal = normalize(local_normal);

	float I = ambient;

	// FIXME: Ensure proper comparison sign
	if (dot(sun_dir, normal) > 0) {
		I += dot(sun_dir, normal) * diffuse;
	}

	gl_FragColor.a = 1;

	gl_FragColor.rgb = I * color;
}
