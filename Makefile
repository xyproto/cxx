.PHONY: clean generate install_pymake src/Makefile src/pymake/make.py src/sakemake uninstall uninstall_pymake unpatch

NAME := sakemake
ALIAS := sm

# the directory of this Makefile
ROOTDIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

SRCDIR := ${ROOTDIR}/src

# macOS detection
UNAME_S := $(shell uname -s)
PYMAKE ?= ${SRCDIR}/pymake/make.py
ifeq ($(UNAME_S),Darwin)
  PREFIX ?= /usr/local
  PYMAKE ?= ${PREFIX}/pymake/make.py
else ifeq ($(UNAME_S),FreeBSD)
  PREFIX ?= /usr/local
  PYMAKE ?= ${PREFIX}/pymake/make.py
else
  PREFIX ?= /usr
  PYMAKE ?= ${PREFIX}/pymake/make.py
endif

VERSION := $(shell grep -F '* Version: ' README.md | cut -d' ' -f3)

# used by the "pkg" target
ifeq ($$pkgdir,)
  pkgdir := $$pkgdir
else
  pkgdir ?= ${PWD}/pkg
endif

generate: src/Makefile src/sakemake src/pymake/make.py

src/Makefile: src/Makefile.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@PYMAKE@@,${PYMAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

src/sakemake: src/sakemake.in
	@sed "s,@@PREFIX@@,${PREFIX},g;s,@@PYMAKE@@,${PYMAKE},g;s,@@VERSION@@,${VERSION},g" $< > $@

src/pymake/make.py:
	@sed 's/env python$$/env python2/g' -i $@

unpatch:
	@sed 's/env python2$$/env python/g' -i src/pymake/make.py

install_pymake:
	@cp -r "${SRCDIR}/pymake" "${DESTDIR}${PREFIX}/share/${NAME}/"
	@rm -rf "${DESTDIR}${PREFIX}/share/${NAME}/pymake/tests"
	@find "${DESTDIR}${PREFIX}/share/${NAME}" -type d -exec chmod 755 {} \;
	@find "${DESTDIR}${PREFIX}/share/${NAME}" -type f -exec chmod 644 {} \;
	@chmod 755 "${DESTDIR}${PREFIX}/share/${NAME}/pymake/make.py"
	@find "${DESTDIR}${PREFIX}/share/${NAME}" -type d -name .git -delete
	@find "${DESTDIR}${PREFIX}/share/${NAME}" -type f -name ".*ignore" -delete

uninstall_pymake:
	@rm -rf "${DESTDIR}${PREFIX}/share/${NAME}/pymake"

install: generate install_pymake unpatch
	@install -d "${DESTDIR}${PREFIX}/bin"
	@install -m755 "${SRCDIR}/${NAME}" "${DESTDIR}${PREFIX}/bin/${NAME}"
	@ln -sf "${PREFIX}/bin/${NAME}" "${DESTDIR}${PREFIX}/bin/${ALIAS}"
	@install -d "${DESTDIR}${PREFIX}/share/${NAME}"
	@install -m644 "${SRCDIR}/Makefile" "${DESTDIR}${PREFIX}/share/${NAME}/Makefile"
	@install -m644 "${SRCDIR}/SConstruct" "${DESTDIR}${PREFIX}/share/${NAME}/SConstruct"
	@install -d "${DESTDIR}${PREFIX}/share/licenses/${NAME}"
	@install -m644 "${ROOTDIR}/LICENSE" "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE"

uninstall: uninstall_pymake
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
