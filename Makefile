.PHONY: uninstall

DESTDIR ?=

# macOS detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  PREFIX ?= /usr/local
else
  PREFIX ?= /usr
endif

all:
	@sed "s,@@PREFIX@@,${PREFIX},g" src/sakemake.in > src/sakemake

install:
	@install -d "${DESTDIR}${PREFIX}/bin"
	@install -m755 src/sakemake "${DESTDIR}${PREFIX}/bin/sakemake"
	@ln -sf ${PREFIX}/bin/sakemake "${DESTDIR}${PREFIX}/bin/sm"
	@install -d "${DESTDIR}${PREFIX}/share/sakemake"
	@install -m644 src/Makefile "${DESTDIR}${PREFIX}/share/sakemake/Makefile"
	@install -m644 src/SConstruct "${DESTDIR}${PREFIX}/share/sakemake/SConstruct"

uninstall:
	@-rm "${DESTDIR}${PREFIX}/bin/sakemake"
	@-rm "${DESTDIR}${PREFIX}/bin/sm"
	@-rm "${DESTDIR}${PREFIX}/share/sakemake/Makefile"
	@-rm "${DESTDIR}${PREFIX}/share/sakemake/SConstruct"
	@-rmdir "${DESTDIR}${PREFIX}/share/sakemake"

clean:
	@-rm src/sakemake
