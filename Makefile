.PHONY: all clean uninstall

NAME := sakemake
ALIAS := sm

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
pkgdir ?= pkg

all: src/${NAME} src/Makefile

src/${NAME}: src/${NAME}.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@MAKE@@,${MAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

src/Makefile: src/Makefile.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@MAKE@@,${MAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

install: src/${NAME} src/Makefile
	@install -d "${DESTDIR}${PREFIX}/bin"
	@install -m755 src/${NAME} "${DESTDIR}${PREFIX}/bin/${NAME}"
	@ln -sf ${PREFIX}/bin/${NAME} "${DESTDIR}${PREFIX}/bin/${ALIAS}"
	@install -d "${DESTDIR}${PREFIX}/share/${NAME}"
	@install -m644 src/Makefile "${DESTDIR}${PREFIX}/share/${NAME}/Makefile"
	@install -m644 src/SConstruct "${DESTDIR}${PREFIX}/share/${NAME}/SConstruct"
	@install -d "${DESTDIR}${PREFIX}/share/licenses/${NAME}"
	@install -m644 LICENSE "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE"

uninstall:
	@-rm "${DESTDIR}${PREFIX}/bin/${NAME}"
	@-rm "${DESTDIR}${PREFIX}/bin/${ALIAS}"
	@-rmdir "${DESTDIR}${PREFIX}/bin"
	@-rm "${DESTDIR}${PREFIX}/share/${NAME}/Makefile"
	@-rm "${DESTDIR}${PREFIX}/share/${NAME}/SConstruct"
	@-rmdir "${DESTDIR}${PREFIX}/share/${NAME}"
	@-rm "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE"
	@-rmdir "${DESTDIR}${PREFIX}/share/licenses/${NAME}"

clean:
	@-rm -f "src/${NAME}" src/Makefile

# like install, but override DESTDIR in order to place everything in "${pkgdir}"
pkg: DESTDIR := ${pkgdir}
pkg: install
