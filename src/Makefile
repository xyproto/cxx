.PHONY: all build opt extra testbuild test clang clangextra clangdebug debug run clean rebuild

clang ?= 0
extra ?= 0
debug ?= 0
opt ?= 0

THIS_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# macOS detection
#UNAME_S := $(shell uname -s)
#ifeq ($(UNAME_S),Darwin)
#  macos ?= 1
#else
#  macos ?= 0
#endif

all: build

build:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=${clang} extra=${extra} debug=${debug} opt=${opt} \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=${clang} extra=${extra} debug=${debug} opt=${opt}

opt:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q opt=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q opt=1 

extra:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q extra=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild extra=1 

testbuild:
	@scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=${clang} extra=${extra} debug=${debug} opt=${opt}

test:
	@scons --file=${THIS_DIR}/SConstruct -Q test clang=${clang} extra=${extra} debug=${debug} opt=${opt}

clang:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1

clangextra:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 extra=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1 extra=1 

clangdebug:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q clang=1 debug=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild clang=1 debug=1 

debug:
	@test -f main.cpp \
	  && scons --file=${THIS_DIR}/SConstruct -Q debug=1 \
	  || scons --file=${THIS_DIR}/SConstruct -Q testbuild debug=1

run:
	@scons --file=${THIS_DIR}/SConstruct -Q run clang=${clang} extra=${extra} debug=${debug} opt=${opt}

rebuild: clean build

clean:
	@scons --file=${THIS_DIR}/SConstruct -Q clean
