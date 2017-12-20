PREFIX ?= /

all:
	@echo 'Usage: PREFIX=/ make install'

install:
	install -Dm755 src/sakemake ${PREFIX}usr/bin/sakemake
	install -Dm644 src/Makefile ${PREFIX}usr/share/sakemake/Makefile
	install -Dm644 src/SConstruct ${PREFIX}usr/share/sakemake/SConstruct

uninstall:
	rm "${PREFIX}usr/bin/sakemake"
	rm "${PREFIX}usr/share/sakemake/Makefile"
	rm "${PREFIX}usr/share/sakemake/SConstruct"
	rmdir "${PREFIX}usr/share/sakemake"
