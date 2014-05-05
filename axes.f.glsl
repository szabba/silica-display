#version 120

uniform vec3 sun;
uniform float ambient;
uniform float diffuse;

varying vec3 local_normal;
varying vec3 local_color;

void main(void) {

	float I_0 = length(sun);

	vec3 sun_dir = normalize(sun);

	float I = ambient;

	//if (dot(sun_dir, local_normal) > 0) {
	//	I += dot(sun_dir, local_normal) * diffuse;
	//}
	gl_FragColor.a = 1;

	gl_FragColor.rgb = I * local_color;
}
