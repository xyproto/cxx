#version 450
#extension GL_ARB_separate_shader_objects : enable

layout(binding = 0) uniform sampler2D tex;

layout(location = 3) in vec3 vpos;
layout(location = 4) in vec3 norm;
layout(location = 5) in vec3 ldir;
layout(location = 6) in vec2 texcoord;

layout(location = 0) out vec4 color;

void main()
{
	vec4 texel = texture(tex, texcoord);

	vec3 vdir = -normalize(vpos);
	vec3 n = normalize(norm);
	vec3 l = normalize(ldir);
	vec3 h = normalize(vdir + ldir);

	float ndotl = max(dot(n, l), 0.0);
	float ndoth = max(dot(n, h), 0.0);

	// XXX (1, 1, 1) diffuse color implied * texel * ndotl
	vec3 diffuse = texel.rgb * ndotl;
	vec3 specular = vec3(1.0, 1.0, 1.0) * pow(ndoth, 50.0);
	// XXX (1, 1, 1) specular color, 50.0 shininess

	// XXX ambient (implied 0) + diffuse + specular
	color.rgb = diffuse + specular;
	color.a = texel.a;
}
