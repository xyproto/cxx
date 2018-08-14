.PHONY: clean

all: frag.spv vert.spv

frag.spv: triangle.frag
	@glslangValidator -V $< -o $@

vert.spv: triangle.vert
	@glslangValidator -V $< -o $@

clean:
	rm -f frag.spv vert.spv

