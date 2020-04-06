#version 420
#extension GL_ARB_separate_shader_objects : enable

layout(std140, binding = 0) uniform matrix_state {
	mat4 vmat;
	mat4 projmat;
	mat4 mvmat;
	mat4 mvpmat;
	vec3 light_pos;
} matrix;


layout(location = 0) in vec4 attr_vertex;
layout(location = 1) in vec3 attr_normal;
layout(location = 2) in vec2 attr_texcoord;

layout(location = 3) out vec3 vpos;
layout(location = 4) out vec3 norm;
layout(location = 5) out vec3 ldir;
layout(location = 6) out vec2 texcoord;

void main()
{
	gl_Position = matrix.mvpmat * attr_vertex;
	vpos = (matrix.mvmat * attr_vertex).xyz;
	norm = mat3(matrix.mvmat) * attr_normal;

	texcoord = attr_texcoord * vec2(2.0, 1.0);

	ldir = matrix.light_pos - vpos;
}

