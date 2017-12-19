PREFIX ?= /

all:
	@echo 'Usage: PREFIX=/ make install'

install:
	install -Dm755 src/snakemake ${PREFIX}usr/bin/snakemake
	install -Dm644 src/Makefile ${PREFIX}usr/share/snakemake/Makefile
	install -Dm644 src/SConstruct ${PREFIX}usr/share/snakemake/SConstruct

uninstall:
	rm "${PREFIX}usr/bin/snakemake"
	rm "${PREFIX}usr/share/snakemake/Makefile"
	rm "${PREFIX}usr/share/snakemake/SConstruct"
	rmdir "${PREFIX}usr/share/snakemake"
