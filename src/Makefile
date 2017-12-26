.PHONY: all build clang clangdebug clangsloppy clangstrict clean debug export opt rebuild run sloppy strict test testbuild version

clang ?= 0
strict ?= 0
debug ?= 0
opt ?= 0
sloppy ?= 0
std ?= c++17
CXX ?=

# macOS detection, for setting the default PREFIX
ifeq ($(shell uname -s),Darwin)
  PREFIX ?= /usr/local
else
  PREFIX ?= /usr
endif

# the name of the installed executable and related directories
NAME ?= $(shell basename $(CURDIR))

# the directory of this Makefile
THIS_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# used by the "pkg" target
pkgdir ?= pkg

all: build

version:
	@echo sakemake 1.9
	@make --version | head -1
	@scons --version | head -2

build:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

opt:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q opt=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q opt=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

strict:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q strict=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild strict=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

sloppy:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q sloppy=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild sloppy=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

testbuild:
	@scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

test:
	@scons --file="${THIS_DIR}/SConstruct" -Q test clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

clang:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

clangstrict:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct "-Q clang=1 strict=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 strict=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

clangsloppy:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 sloppy=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 sloppy=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

clangdebug:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 debug=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 debug=1 std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

debug:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q debug=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild debug=1 clang=${clang} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

run:
	@scons --file="${THIS_DIR}/SConstruct" -Q run clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

rebuild: clean build

clean:
	@scons --file="${THIS_DIR}/SConstruct" -Q clean

main: main.cpp
	@scons --file="${THIS_DIR}/SConstruct" -Q clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} std=${std} CXX=${CXX} CXXFLAGS=${CXXFLAGS}

# install the executable, data/*, img/*, resources/* or share/* into a shared directory, also install the license, if available
install: main
	@install -d "${DESTDIR}${PREFIX}/bin"
	@install -m755 main "${DESTDIR}${PREFIX}/bin/${NAME}"
	@install -d "${DESTDIR}${PREFIX}/share/${NAME}"
	@test -d data && cp -r data/* "${DESTDIR}${PREFIX}/share/${NAME}/" || true
	@test -d img && cp -r img/* "${DESTDIR}${PREFIX}/share/${NAME}/" || true
	@test -d resources && cp -r resources/* "${DESTDIR}${PREFIX}/share/${NAME}/" || true
	@test -d share && cp -r share/* "${DESTDIR}${PREFIX}/share/${NAME}/" || true
	@test -f COPYING && install -d "${DESTDIR}${PREFIX}/share/licenses/${NAME}" && install -m644 COPYING "${DESTDIR}${PREFIX}/share/licenses/${NAME}/COPYING" || true
	@test -f LICENSE && install -d "${DESTDIR}${PREFIX}/share/licenses/${NAME}" && install -m644 LICENSE "${DESTDIR}${PREFIX}/share/licenses/${NAME}/LICENSE" || true
	@-rmdir --ignore-fail-on-non-empty "${DESTDIR}${PREFIX}/share/${NAME}"
	@-rmdir --ignore-fail-on-non-empty "${DESTDIR}${PREFIX}/share"

# like install, but override DESTDIR in order to place everything in "${pkgdir}"
pkg: DESTDIR := ${pkgdir}
pkg: install

export:
	@cp -i -v "${THIS_DIR}/Makefile" "${THIS_DIR}/SConstruct" .
