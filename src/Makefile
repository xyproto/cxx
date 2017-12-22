.PHONY: all build opt strict sloppy testbuild test clang clangstrict clangsloppy clangdebug debug run clean rebuild

clang ?= 0
strict ?= 0
debug ?= 0
opt ?= 0
sloppy ?= 0

# macOS detection, for setting the default PREFIX
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  PREFIX ?= /usr/local
else
  PREFIX ?= /usr
endif

# the name of the installed executable and related directories
NAME ?= $(shell basename $(CURDIR))

# the directory of this Makefile
THIS_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

all: build

build:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy} \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy}

opt:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q opt=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q opt=1

strict:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q strict=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild strict=1

sloppy:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q sloppy=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild sloppy=1

testbuild:
	@scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy}

test:
	@scons --file="${THIS_DIR}/SConstruct" -Q test clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy}

clang:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1

clangstrict:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct "-Q clang=1 strict=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 strict=1

clangsloppy:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 sloppy=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 sloppy=1

clangdebug:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q clang=1 debug=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild clang=1 debug=1

debug:
	@test -f main.cpp \
	  && scons --file="${THIS_DIR}/SConstruct" -Q debug=1 \
	  || scons --file="${THIS_DIR}/SConstruct" -Q testbuild debug=1

run:
	@scons --file="${THIS_DIR}/SConstruct" -Q run clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy}

rebuild: clean build

clean:
	@scons --file="${THIS_DIR}/SConstruct" -Q clean

main: main.cpp
	@scons --file="${THIS_DIR}/SConstruct" -Q clang=${clang} strict=${strict} debug=${debug} opt=${opt} sloppy=${sloppy}

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
	@-rmdir "${DESTDIR}${PREFIX}/share/${NAME}"
