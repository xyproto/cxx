.PHONY: clean generate uninstall src/Makefile src/sakemake

NAME := sakemake
ALIAS := sm

# the directory of this Makefile
ROOTDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

SRCDIR := ${ROOTDIR}/src

# macOS detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  PREFIX ?= /usr/local
  MAKE ?= make
else ifeq ($(UNAME_S),FreeBSD)
  PREFIX ?= /usr/local
  MAKE ?= gmake
else
  PREFIX ?= /usr
  MAKE ?= make
endif

VERSION := $(shell grep -F '* Version: ' README.md | cut -d' ' -f3)

# used by the "pkg" target
ifeq ($$pkgdir,)
  pkgdir := $$pkgdir
else
  pkgdir ?= ${PWD}/pkg
endif

generate: src/Makefile src/sakemake

src/Makefile: src/Makefile.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@MAKE@@,${MAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

src/sakemake: src/sakemake.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@MAKE@@,${MAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

install: generate
	@install -d "${DESTDIR}${PREFIX}/bin"
	@install -m755 "${SRCDIR}/${NAME}" "${DESTDIR}${PREFIX}/bin/${NAME}"
	@ln -sf "${PREFIX}/bin/${NAME}" "${DESTDIR}${PREFIX}/bin/${ALIAS}"
	@install -d "${DESTDIR}${PREFIX}/share/${NAME}"
	@install -m644 "${SRCDIR}/Makefile" "${DESTDIR}${PREFIX}/share/${NAME}/Makefile"
	@install -m644 "${SRCDIR}/SConstruct" "${DESTDIR}${PREFIX}/share/${NAME}/SConstruct"
	@install -d "${DESTDIR}${PREFIX}/share/licenses/${NAME}"
	@install -m644 "${ROOTDIR}/LICENSE" "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE"

uninstall:
	@-rm -f "${DESTDIR}${PREFIX}/bin/${NAME}"
	@-rm -f "${DESTDIR}${PREFIX}/bin/${ALIAS}"
	@-rmdir "${DESTDIR}${PREFIX}/bin" 2>/dev/null || true
	@-rm -f "${DESTDIR}${PREFIX}/share/${NAME}/Makefile"
	@-rm -f "${DESTDIR}${PREFIX}/share/${NAME}/SConstruct"
	@-rmdir "${DESTDIR}${PREFIX}/share/${NAME}" 2>/dev/null || true
	@-rm -f "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE"
	@-rmdir "${DESTDIR}${PREFIX}/share/licenses/${NAME}" 2>/dev/null || true

clean:
	@-rm -f src/Makefile src/sakemake

# like install, but override DESTDIR in order to place everything in "${pkgdir}"
pkg: DESTDIR ?= ${pkgdir}
pkg: install
