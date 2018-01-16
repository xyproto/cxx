#!/bin/sh

# input: gtk/gtk.h
# output: a long list of build flags, some for gtk2, some for gtk3

for pkg in $(grep -l -r $(find /usr/include/ -wholename "*/gtk/gtk.h" | sed 's,/gtk/gtk.h,,g;s,/usr/include,${includedir},g') /usr/lib/pkgconfig | sort -V | cut -d"/" -f5 | sed "s,.pc,,g"); do pkg-config --libs --cflags $pkg; done | sort -V
