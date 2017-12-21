.PHONY: all build opt extra testbuild test clang clangextra clangdebug debug run clean rebuild

clang ?= 0
extra ?= 0
debug ?= 0
opt ?= 0

THIS_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# macOS detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  macos ?= 1
else
  macos ?= 0
endif

all: build

build:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=${clang} extra=${extra} debug=${debug} opt=${opt} macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=${clang} extra=${extra} debug=${debug} opt=${opt} macos=${macos}

opt:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q opt=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q opt=1 macos=${macos}

extra:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q extra=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild extra=1 macos=${macos}

testbuild:
	@scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=${clang} extra=${extra} debug=${debug} opt=${opt} macos=${macos}

test:
	@scons --file=${THIS_DIR}/SConstruct -Q test clang=${clang} extra=${extra} debug=${debug} opt=${opt} macos=${macos}

clang:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1 macos=${macos}

clangextra:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 extra=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1 extra=1 macos=${macos}

clangdebug:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 debug=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1 debug=1 macos=${macos} 

debug:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q debug=1 macos=${macos} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild debug=1 macos=${macos}

run:
	@scons --file=${THIS_DIR}/SConstruct -Q run clang=${clang} extra=${extra} debug=${debug} opt=${opt} macos=${macos}

rebuild: clean build

clean:
	@scons --file=${THIS_DIR}/SConstruct -Q clean macos=${macos}
