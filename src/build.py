#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import os.path
import platform
from commands import getstatusoutput
from glob import iglob
from itertools import chain
from multiprocessing import cpu_count
from subprocess import check_output
from sys import argv, exit, stdout
from urllib import quote

LOCAL_COMMON_PATHS = ["common", "Common", "../common", "../Common"]
LOCAL_INCLUDE_PATHS = [".", "include", "Include", "..", "../include", "../Include"] + LOCAL_COMMON_PATHS
PATHLIST = os.environ["PATH"].split(os.pathsep)  # split on ":"
SPECIAL_SYMBOLS = "@@@@@"  # string that is unlikely to appear in an include line or a build flag
# skip compilation-related packages when searching for includes
SKIP_PACKAGES = ["glibc", "gcc", "wine"]

cached_pc_files = {}


def hints(missing_includes):
    """Output hints for how to configure missing includes on some platforms"""
    if platform.system() == "Darwin" and "GL/glut.h" in missing_includes:
        print("""
NOTE: On macOS, include GLUT/glut.h instead of GL/glut.h.

Suggested code:

    #ifdef __APPLE__
    #include <GLUT/glut.h>
    #else
    #include <GL/glut.h>
    #endif
""")
    if platform.system() == "Darwin" and "GL/gl.h" in missing_includes:
        print("""
NOTE: On macOS, include OpenGL/gl.h instead of GL/gl.h.

Suggested code:

    #ifdef __APPLE__
    #include <OpenGL/gl.h>
    #else
    #include <GL/gl.h>
    #endif
""")


def exe(fpath):
    """Check if the given path/filename both exists and is executable."""
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    """Check if a program exists in PATH"""
    fpath, fname = os.path.split(program)
    if fpath:
        exe_file = program
        # Check if the file exists and is executable
        if exe(exe_file):
            return exe_file
    else:
        for path in PATHLIST:
            exe_file = os.path.join(path, program)
            # Check if the file exists and is executable
            if exe(exe_file):
                return exe_file
    return None


def split_cxxflags(given_cxxflags, win64):
    """Split a list of flags into includes (-I...), defines (-D...), libs (-l...), lib paths (-L...), linkflags (-Wl,) and other flags (-p, -F, -framework)"""
    includes = " "
    defines = " "
    libs = " "
    libpaths = " "
    linkflags = " "
    other = " "
    encountered_framework = False

    # Note that -Wl,-framework may appear in the given_cxxflags
    for flag in [f.strip() for f in given_cxxflags.replace(" -framework ", " -framework" + SPECIAL_SYMBOLS).split(" ")]:
        if flag.startswith("-I"):
            if " " + flag[2:] + " " not in includes:
                includes += flag[2:] + " "
        elif flag.startswith("-D"):
            if " " + flag[2:] + " " not in defines:
                defines += flag[2:] + " "
        elif flag.startswith("-l"):
            if " " + flag[2:] + " " not in libs:
                libs += flag[2:] + " "
        elif flag.startswith("-L"):
            if " " + flag + " " not in libpaths:
                libpaths += flag + " "
        elif flag.startswith("-Wl,"):
            if (" " + flag + " " not in linkflags) and not (win64 and "-framework" in flag):
                linkflags += flag + " "
        elif flag.startswith("-p"):
            if " " + flag + " " not in other:
                other += flag + " "
        elif flag.lower().startswith("-f"):
            new_flag = flag.replace("-framework" + SPECIAL_SYMBOLS, "-framework ")
            if not win64 and (" " + new_flag + " " not in linkflags):
                if "-framework" in new_flag:
                    encountered_framework = True
                linkflags += new_flag + " "
            elif win64:
                new_dll = new_flag[len("-framework "):] + ".dll"
                # new_dll now contains a case-insensitive name. See if there is .dll with the same name but different casing, then use that
                for dll in chain(iglob("*.dll"), iglob("*.DLL")):
                    if dll.lower() == new_dll.lower():
                        new_dll = dll
                        break
                new_linkflag = "-l" + new_dll[:-4]
                if " " + new_linkflag + " " not in linkflags and new_linkflag != "-lFrameworks":
                    linkflags += new_linkflag + " "
                if "-L." not in linkflags:
                    linkflags += "-L. "
        elif flag.startswith("-stdlib"):
            if " " + flag + " " not in linkflags:
                linkflags += flag + " "
            if " " + flag + " " not in other:
                other += flag + " "
        elif not win64 and encountered_framework and (not flag.startswith("-")) and ("." not in flag):
            # the pkg-config output for Qt libraries list several frameworks after a single "-framework" parameter
            new_flag = "-framework " + flag
            if " " + new_flag + " " not in linkflags:
                linkflags += new_flag + " "
        elif flag.startswith("-W"):
            # related to warnings
            if " " + flag + " " not in other:
                other += flag + " "
        else:
            # Only includes, defines, libraries, library paths and linkflags are supported
            print("WARNING: Unsupported flag for configuring packages: " + flag)
            continue
    # Other CXXFLAGS can be returned as the final value here
    return includes.strip(), defines.strip(), libs.strip(), libpaths.strip(), linkflags.strip(), other.strip()


def generic_include_path_to_cxxflags(include_path):
    """Takes a path to a header file and returns cxxflags, or an empty string.
    For unfamiliar Linux distros where a package manager and pkg-config are not available."""

    if include_path == "":
        return ""

    # Guess the name of the package
    try:
        package_guess = include_path.split(os.path.sep)[3]
    except IndexError:
        return ""
    # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
    booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
    # List of possible package names, used when searching for .so files below
    packages = [package_guess, booststyle, package_guess.lower()]
    if not packages:
        return ""
    for package in packages:
        if package in SKIP_PACKAGES:
            return ""
    # If a library matches the name of the directory in the system include directory, link with that
    for package in packages:
        for possible_lib_name in ["lib" + package + ".so", "lib" + package.upper() + ".so"]:
            for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/pkg/lib"]:
                if os.path.exists(libpath) and os.path.exists(os.path.join(libpath, possible_lib_name)):
                    # Check if the same library with a ++ suffix also exists
                    if os.path.exists(os.path.join(libpath, possible_lib_name.replace(".so", "++.so"))):
                        # Found two good candidates, the regular ".so" lib and the "++.so" lib
                        # Example: -lfcgi -lfcgi++
                        return "-l" + possible_lib_name[3:-3] + " -l" + possible_lib_name[3:-3] + "++"
                    # Found a good candidate, matching the name of the package that owns the include file. Try that.
                    return "-l" + possible_lib_name[3:-3]
    # Out of ideas
    return ""


def arch_recommend_package(missing_include):
    """Given a missing include file, print out a message for a package that could be installed and exit with error code 1, or else just return."""
    if missing_include == "":
        return
    # Check if the given include file is missing from the system
    if not os.path.exists(missing_include):
        if which("pkgfile"):
            cmd = "LC_ALL=C pkgfile " + missing_include
            try:
                packages = os.popen2(cmd)[1].read().strip().split("\n")
            except OSError:
                packages = []
            for package in packages:
                if package:
                    if "/" in package:
                        # strip away leading "extra/" or "community/"
                        package = package.split("/")[1]
                    if package in SKIP_PACKAGES:
                        return
                    print("\nerror: Could not find \"" + missing_include +
                          "\", install with: pacman -S " + package + "\n")
                    exit(1)
        else:
            print("\nerror: Could not find \"" + missing_include +
                  "\". Having pkgfile would help, try: pacman -S pkgfile\n")
            exit(1)
        return


def arch_include_path_to_cxxflags(include_path):
    """Takes a path to a header file and returns cxxflags, or an empty string.
    For Arch Linux."""
    if include_path == "":
        return ""
    # Check if the given include file is missing from the system
    if not os.path.exists(include_path):
        return ""
    # Find the package that owns the include directory in question
    cmd = 'LC_ALL=C /usr/bin/pacman -Qo ' + include_path + ' | /usr/bin/cut -d" " -f5'
    try:
        package = os.popen2(cmd)[1].read().strip()
    except OSError:
        package = ""
    if not package:
        print("error: No package owns: " + include_path)
        exit(1)
    if package in SKIP_PACKAGES:
        return ""
    cmd = '/usr/bin/pacman -Ql ' + package + ' | /usr/bin/grep "\.pc$" | /usr/bin/cut -d" " -f2-'
    if package in cached_pc_files:
        pc_files = cached_pc_files[package]
    else:
        try:
            pc_files = [x for x in os.popen2(cmd)[1].read().strip().split(os.linesep) if x]
            cached_pc_files[package] = pc_files
        except OSError:
            pc_files = []
    if not pc_files:
        # If a library in /usr/lib matches the name of the package without .pc files, link with that
        libpath = "/usr/lib"
        # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
        booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
        for possible_lib_name in [package, booststyle, package.upper(), os.path.splitext(os.path.basename(include_path))[0]]:
            if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + ".so")):
                # Found a good candidate, matching the name of the package that owns the include file. Try that.
                retval = "-l" + possible_lib_name
                if os.path.exists(os.path.dirname(include_path)):
                    # Also found an include directory
                    retval += " -I" + os.path.dirname(include_path)
                # TODO: Add the check for "++" libs to the other distros as well
                if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + "++.so")):
                    # Also found a ++.so file
                    retval += " -l" + possible_lib_name + "++"
                return retval
        # Did not find a suitable library file, nor .pc file
        if package != "boost":  # boost is "special"
            print("WARNING: No pkg-config files for: " + package)
        return ""
    # TODO: Consider interpreting the .pc files directly, for speed
    all_cxxflags = ""
    for pc_file in pc_files:
        pc_name = os.path.splitext(os.path.basename(pc_file))[0]
        cmd = '/usr/bin/pkg-config --cflags --libs ' + pc_name + ' 2>/dev/null'
        # Get the cxxflags as defined by pkg-config
        cxxflags = ""
        try:
            cxxflags = os.popen2(cmd)[1].read().strip()
        except OSError:
            pass
        if not cxxflags:
            # pkg-config did not work! Print a warning and just guess the flag.
            if cmd.endswith("2>/dev/null"):
                cmd = cmd[:-11]
            # Output the pkg-config command
            print("warning: this command failed to run:\n" + cmd)
            # Just guess the library flag
            cxxflags = "-l" + pc_name
        if cxxflags:
            for cxxflag in cxxflags.split(" "):
                if cxxflag not in all_cxxflags.split(" "):
                    all_cxxflags += " " + cxxflag

    return all_cxxflags.strip()


def freebsd_recommend_package(missing_include):
    """Given a missing include file, print out a message for a package that could be installed and exit with error code 1, or else just return."""
    if missing_include == "":
        return
    # Check if the given include file is missing from the system
    if not os.path.exists(missing_include):
        if exe("/usr/local/bin/curl"):
            last_part = os.path.basename(missing_include)
            cmd = '/usr/local/bin/curl -s "http://www.secnetix.de/tools/porgle/porgle.py?plst=1&q=' + quote(last_part) + \
                '&Search=Search" | grep "td " | grep small | cut -d">" -f4- | cut -d"-" -f1'
            try:
                packages = [x.strip() for x in os.popen2(cmd)[1].read().strip().split("\n")
                            if x.strip() and x.strip() not in SKIP_PACKAGES]
            except OSError:
                packages = []
            if packages:
                print("\nerror: Could not find package for missing include \"" +
                      missing_include + "\".\n       It could belong to one of these:")
                for package in packages:
                    print(" " * 11 + package)
                exit(1)
        return


def freebsd_include_path_to_cxxflags(include_path):
    """Takes a path to a header file and returns cxxflags, or an empty string.
    For FreeBSD."""
    if include_path == "":
        return ""
    # Check if the given include file is missing from the system
    if not os.path.exists(include_path):
        return ""
    # Find the package that owns the include directory in question
    cmd = '/usr/sbin/pkg which -q ' + include_path + ' | cut -d- -f1-'
    try:
        package = os.popen2(cmd)[1].read().strip()
    except OSError:
        package = ""
    if not package:
        print("error: No package owns: " + include_path)
        exit(1)
    if package in SKIP_PACKAGES:
        return ""
    if package in cached_pc_files:
        pc_files = cached_pc_files[package]
    else:
        cmd = "/usr/sbin/pkg list " + package + " | /usr/bin/grep '\.pc$'"
        try:
            pc_files = [x for x in os.popen2(cmd)[1].read().strip().split(os.linesep) if x]
            cached_pc_files[package] = pc_files
        except OSError:
            pc_files = []
    if not pc_files:
        # If a library in /usr/local/lib matches the name of the package without .pc files, link with that
        libpath = "/usr/local/lib"
        # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
        booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
        for possible_lib_name in [package, booststyle, package.upper(), os.path.splitext(os.path.basename(include_path))[0]]:
            if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + ".so")):
                # Found a good candidate, matching the name of the package that owns the include file. Try that.
                if os.path.exists(os.path.dirname(include_path)):
                    # Also found an include directory
                    return "-l" + possible_lib_name + " -I" + os.path.dirname(include_path)
                return "-l" + possible_lib_name
        # Did not find a suitable library file, nor .pc file
        if package != "boost":  # boost is "special"
            print("WARNING: No pkg-config files for: " + package)
        return ""
    # TODO: Consider interpreting the .pc files directly, for speed
    all_cxxflags = ""
    for pc_file in pc_files:
        pc_name = os.path.splitext(os.path.basename(pc_file))[0]
        cmd = '/usr/local/bin/pkg-config --cflags --libs ' + pc_name + ' 2>/dev/null'
        # Get the cxxflags as defined by pkg-config
        cxxflags = ""
        try:
            cxxflags = os.popen2(cmd)[1].read().strip()
        except OSError:
            # Let cxxflags remain empty
            pass
        if not cxxflags:
            # pkg-config did not work! Print a warning and just guess the flag.
            if cmd.endswith("2>/dev/null"):
                cmd = cmd[:-11]
            # Output the pkg-config command
            print("warning: this command failed to run:\n" + cmd)
            # Just guess the library flag
            cxxflags = "-l" + pc_name
        if cxxflags:
            for cxxflag in cxxflags.split(" "):
                if cxxflag not in all_cxxflags.split(" "):
                    all_cxxflags += " " + cxxflag
    return all_cxxflags.strip()


def openbsd_include_path_to_cxxflags(include_path):
    """Takes a path to a header file and returns cxxflags, or an empty string.
    For OpenBSD."""
    if include_path == "":
        return ""
    # Check if the given include file is missing from the system
    if not os.path.exists(include_path):
        return ""
    # Find the package that owns the include directory in question
    cmd = '/usr/sbin/pkg_info -E ' + include_path + ' | head -1 | cut -d" " -f2 | cut -d- -f1'
    try:
        package = os.popen2(cmd)[1].read().strip()
    except OSError:
        package = ""
    if not package:
        print("error: No package owns: " + include_path)
        exit(1)
    if package in SKIP_PACKAGES:
        return ""
    if package in cached_pc_files:
        pc_files = cached_pc_files[package]
    else:
        cmd = "/usr/sbin/pkg_info -L " + package + " | grep \"\\.pc\""
        try:
            pc_files = [x for x in os.popen2(cmd)[1].read().strip().split(os.linesep) if x]
            cached_pc_files[package] = pc_files
        except OSError:
            pc_files = []
    if not pc_files:
        # If a library in /usr/local/lib matches the name of the package without .pc files, link with that
        libpath = "/usr/local/lib"
        # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
        booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
        for possible_lib_name in [package, booststyle, package.upper(), os.path.splitext(os.path.basename(include_path))[0]]:
            if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + ".so")):
                # Found a good candidate, matching the name of the package that owns the include file. Try that.
                if os.path.exists(os.path.dirname(include_path)):
                    # Also found an include directory
                    return "-l" + possible_lib_name + " -I" + os.path.dirname(include_path)
                return "-l" + possible_lib_name
        # Did not find a suitable library file, nor .pc file
        if package != "boost":  # boost is "special"
            print("WARNING: No pkg-config files for: " + package)
        return ""
    # TODO: Consider interpreting the .pc files directly, for speed
    all_cxxflags = ""
    for pc_file in pc_files:
        pc_name = os.path.splitext(os.path.basename(pc_file))[0]
        cmd = '/usr/bin/pkg-config --cflags --libs ' + pc_name + ' 2>/dev/null'
        # Get the cxxflags as defined by pkg-config
        cxxflags = ""
        try:
            cxxflags = os.popen2(cmd)[1].read().strip()
        except OSError:
            # Let cxxflags remain empty
            pass
        if not cxxflags:
            # pkg-config did not work! Print a warning and just guess the flag.
            if cmd.endswith("2>/dev/null"):
                cmd = cmd[:-11]
            # Output the pkg-config command
            print("warning: this command failed to run:\n" + cmd)
            # Just guess the library flag
            cxxflags = "-l" + pc_name
        if cxxflags:
            for cxxflag in cxxflags.split(" "):
                if cxxflag not in all_cxxflags.split(" "):
                    all_cxxflags += " " + cxxflag
    return all_cxxflags.strip()


def deb_recommend_package(missing_include):
    """Given a missing include file, print out a message for a package that could be installed and exit with error code 1, or else just return."""
    if missing_include == "":
        return
    # Check if the given include file is missing from the system
    if not os.path.exists(missing_include):
        if which("apt-file"):
            cmd = "LC_ALL=C apt-file find -Fl " + missing_include
            try:
                package = os.popen2(cmd)[1].read().strip()
            except OSError:
                package = ""
            if package in SKIP_PACKAGES:
                return
            if package:
                print("\nerror: Could not find \"" + missing_include +
                      "\", install with: apt install " + package + "\n")
                exit(1)
        else:
            print("\nerror: Could not find \"" + missing_include +
                  "\". Having apt-file would help, try: apt install apt-file\n")
            exit(1)
        return


def deb_include_path_to_cxxflags(include_path, cxx="g++"):
    """Takes a path to a header file and returns cxxflags, or an empty string
    For Debian/Ubuntu."""
    if include_path == "":
        return ""
    if not os.path.exists(include_path):
        return ""
    # Find the package that owns the include directory in question
    cmd = 'LC_ALL=C /usr/bin/dpkg-query -S ' + include_path + ' | /usr/bin/cut -d: -f1'
    try:
        package = os.popen2(cmd)[1].read().strip()
    except OSError:
        package = ""
    if not package:
        print("error: No package owns: " + include_path)
        exit(1)
    if package in SKIP_PACKAGES:
        return ""
    cmd = 'LC_ALL=C /usr/bin/dpkg-query -L ' + package + ' | /bin/grep "\.pc$"'
    if package in cached_pc_files:
        pc_files = cached_pc_files[package]
    else:
        try:
            pc_files = [x for x in os.popen2(cmd)[1].read().strip().split(os.linesep) if x]
            cached_pc_files[package] = pc_files
        except OSError:
            pc_files = []
    if not pc_files:
        machine_name = os.popen2(cxx + " -dumpmachine")[1].read().strip()
        # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
        booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
        # If a library in one of the library paths matches the name of the package without .pc files, link with that
        for possible_lib_name in [package, booststyle, package.upper(), os.path.splitext(os.path.basename(include_path))[0]]:
            for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/lib/" + machine_name]:
                if os.path.exists(libpath) and os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + ".so")):
                    # Found a good candidate, matching the name of the package that owns the include file. Try that.
                    retval = "-l" + possible_lib_name
                    if os.path.exists(os.path.dirname(include_path)):
                        # Also found an include directory
                        retval += " -I" + os.path.dirname(include_path)
                    # TODO: Add the check for "++" libs to the other distros as well
                    if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + "++.so")):
                        # Also found a ++.so file
                        retval += " -l" + possible_lib_name + "++"
                    return retval
        # Did not find a suitable library file, nor .pc file
        if package != "boost":  # boost is "special"
            print("WARNING: No pkg-config files for: " + package)
        return ""
    # TODO: Consider interpreting the .pc files directly, for speed
    all_cxxflags = ""
    for pc_file in pc_files:
        pc_name = os.path.splitext(os.path.basename(pc_file))[0]
        cmd = '/usr/bin/pkg-config --cflags --libs ' + pc_name + ' 2>/dev/null'
        # Get the cxxflags as defined by pkg-config
        cxxflags = ""
        try:
            cxxflags = os.popen2(cmd)[1].read().strip()
        except OSError:
            pass
        if not cxxflags:
            # pkg-config did not work! Print a warning and just guess the flag.
            if cmd.endswith("2>/dev/null"):
                cmd = cmd[:-11]
            # Output the pkg-config command
            print("warning: this command failed to run:\n" + cmd)
            # Just guess the library flag
            cxxflags = "-l" + pc_name
        if cxxflags:
            for cxxflag in cxxflags.split(" "):
                if cxxflag not in all_cxxflags.split(" "):
                    all_cxxflags += " " + cxxflag
    return all_cxxflags.strip()


def brew_include_path_to_cxxflags(include_path):
    """Takes a path to a header file and returns cxxflags, or an empty string.
    For macOS/homebrew."""

    if include_path == "":
        return ""
    normpath = os.path.normpath(include_path)
    if not os.path.exists(normpath):
        return ""
    # Follow symlinks
    realpath = os.path.realpath(include_path)

    # Now try to find the package that owns this file
    package = ""
    # If the path now starts with "/usr/local/Cellar/", then success, else return
    if realpath.startswith("/usr/local/Cellar/") and realpath.count(os.path.sep) > 4:
        # OK, found an include file that has been installed by Homebrew, this is promising
        # Strip away "/usr/local/Cellar/" from the start of the path,
        # then use the first word as the package name
        package = realpath[18:].split(os.path.sep)[0]
    else:
        # Try using the first directory after "/usr/local/include" as the package name
        package = include_path.replace("/usr/local/include/", "")
    if not package:
        # Out of guesses
        return ""
    # Check if the guessed package name not be skipped
    if package in SKIP_PACKAGES:
        return ""

    # Get all .pc files that belong to the same package,
    # this also tests if it's a valid package name
    cmd = 'LC_ALL=C brew ls --verbose ' + package + " | grep '\.pc$'"
    if package in cached_pc_files:
        pc_files = cached_pc_files[package]
    else:
        try:
            pc_files = [x for x in os.popen2(cmd)[1].read().strip().split(os.linesep) if x]
            cached_pc_files[package] = pc_files
        except OSError:
            pc_files = []
    if not pc_files:
        # Example: Extract "boost_filesystem" from "/usr/include/boost/filesystem.h"
        booststyle = os.path.splitext("_".join(include_path.split("/")[-2:]))[0]
        # If a library in /usr/local/lib matches the name of the package without .pc files, link with that
        for possible_lib_name in [package, booststyle, package.upper(), os.path.splitext(os.path.basename(include_path))[0]]:
            for libpath in ["/usr/local/lib", "/usr/lib"]:
                if os.path.exists(os.path.join(libpath, "lib" + possible_lib_name + ".so")):
                    # Found a good candidate, matching the name of the package that owns the include file. Try that.
                    if os.path.exists(os.path.dirname(include_path)):
                        # Also found an include directory
                        return "-l" + possible_lib_name + " -I" + os.path.dirname(include_path)
                    return "-l" + possible_lib_name
        # Did not find a suitable library file, nor .pc file
        if package != "boost":  # boost is "special"
            print("WARNING: No pkg-config files for: " + package)
        return ""
    # TODO: Consider interpreting the .pc files directly, for speed
    all_cxxflags = ""
    for pc_file in pc_files:
        pc_name = os.path.splitext(os.path.basename(pc_file))[0]
        pc_dir = os.path.dirname(pc_file)
        cmd = 'PKG_CONFIG_PATH="' + pc_dir + '" pkg-config --cflags --libs ' + pc_name + ' 2>/dev/null'
        # Get the cxxflags as defined by pkg-config
        cxxflags = ""
        try:
            cxxflags = os.popen2(cmd)[1].read().strip()
        except OSError:
            pass
        if not cxxflags:
            # pkg-config did not work! Print a warning and just guess the flag.
            if cmd.endswith("2>/dev/null"):
                cmd = cmd[:-11]
            # Output the pkg-config command
            print("warning: this command failed to run:\n" + cmd)
            # Just guess the library flag
            cxxflags = "-l" + pc_name
        if cxxflags:
            for cxxflag in cxxflags.split(" "):
                if cxxflag not in all_cxxflags.split(" "):
                    all_cxxflags += " " + cxxflag
    return all_cxxflags.strip()


def get_buildflags(sourcefilename, system_include_dirs, win64, compiler_includes, cxx=None):
    """Given a source file, try to extract the relevant includes and get pkg-config to output relevant --cflags and --libs.
    Returns includes, defines, libs, lib paths, linkflags and other cxx flags"""

    if type(system_include_dirs) == type(""):
        print("error: system_include_dirs is supposed to be a list")
        sys.exit(1)

    if sourcefilename == "":
        return "", "", "", "", "", ""

    # Check if pkg-config is in the PATH
    has_pkg_config = bool(which("pkg-config"))
    has_package_manager = False

    # if 'run' not in ARGUMENTS:
    #    print("Discovering build flags for {}... ".format(sourcefilename), end="")
    #    stdout.flush()

    # Filter out include lines, then run cpp
    cmd = "LC_CTYPE=C && LANG=C && sed 's/^#include/" + SPECIAL_SYMBOLS + "include/g' < \"" + \
        sourcefilename + "\" | cpp -E -P -w -pipe | sed 's/^" + SPECIAL_SYMBOLS + "include/#include/g'"
    try:
        source_lines = os.popen2(cmd)[1].read().split(os.linesep)[:-1]
    except:
        print("WARNING: Command failed: " + cmd)
        return "", "", "", "", "", ""
    includes = []
    for line in source_lines:
        if line.strip().startswith("#include"):
            if line.count("<") == 1 and line.count(">") == 1:
                includes.append(line.strip().split("<")[1].split(">")[0])
            elif line.count("\"") == 2:
                includes.append(line.strip().split("\"")[1].split("\"")[0])

    # Skip C99, C++, C++20 and deprecated C++ headers + more
    skiplist = ("assert.h", "complex.h", "ctype.h", "errno.h", "fenv.h", "float.h", "inttypes.h", "iso646.h", "limits.h", "locale.h", "math.h", "setjmp.h", "signal.h", "stdalign.h", "stdarg.h", "stdatomic.h", "stdbool.h", "stddef.h", "stdint.h", "stdio.h", "stdlib.h", "stdnoreturn.h", "string.h", "tgmath.h", "threads.h", "time.h", "uchar.h", "wchar.h", "wctype.h", "cstdlib", "csignal", "csetjmp", "cstdarg", "typeinfo", "typeindex", "type_traits", "bitset", "functional", "utility", "ctime", "chrono", "cstddef", "initializer_list", "tuple", "any", "optional", "variant", "new", "memory", "scoped_allocator", "memory_resource", "climits", "cfloat", "cstring", "cctype",
                "cstdint", "cinttypes", "limits", "exception", "stdexcept", "cassert", "system_error", "cerrno", "array", "vector", "deque", "list", "forward_list", "set", "map", "unordered_set", "unordered_map", "stack", "queue", "algorithm", "execution", "iterator", "cmath", "complex", "valarray", "random", "numeric", "ratio", "cfenv", "iosfwd", "ios", "istream", "ostream", "iostream", "fstream", "sstream", "iomanip", "streambuf", "cstdio", "locale", "clocale", "regex", "atomic", "thread", "mutex", "shared_mutex", "future", "condition_variable", "filesystem", "compare", "charconv", "syncstream", "strstream", "codecvt", "glibc", "string", "windows.h")

    win64skiplist = ("GL/gl.h", "GL/glaux.h", "GL/glcorearb.h", "GL/glext.h", "GL/glu.h", "GL/glxext.h", "GL/wglext.h", "accctrl.h", "aclapi.h", "aclui.h", "activation.h", "activaut.h", "activdbg.h", "activdbg100.h", "activecf.h", "activeds.h", "activprof.h", "activscp.h", "adc.h", "adhoc.h", "admex.h", "adoctint.h", "adodef.h", "adogpool.h", "adogpool_backcompat.h", "adoguids.h", "adoid.h", "adoint.h", "adoint_backcompat.h", "adojet.h", "adomd.h", "adptif.h", "adsdb.h", "adserr.h", "adshlp.h", "adsiid.h", "adsnms.h", "adsprop.h", "adssts.h", "adtgen.h", "advpub.h", "afxres.h", "af_irda.h", "agtctl.h", "agtctl_i.c", "agterr.h", "agtsvr.h", "agtsvr_i.c", "alg.h", "alink.h", "amaudio.h", "amstream.h", "amstream.idl", "amvideo.h", "amvideo.idl", "apdevpkey.h", "apiset.h", "apisetcconv.h", "appmgmt.h", "aqadmtyp.h", "asptlb.h", "assert.h", "atacct.h", "atalkwsh.h", "atsmedia.h", "audevcod.h", "audioapotypes.h", "audioclient.h", "audioendpoints.h", "audioengineendpoint.h", "audiopolicy.h", "audiosessiontypes.h", "austream.h", "austream.idl", "authif.h", "authz.h", "aux_ulib.h", "avifmt.h", "aviriff.h", "avrfsdk.h", "avrt.h", "axextendenums.h", "azroles.h", "basetsd.h", "basetyps.h", "batclass.h", "bcrypt.h", "bdaiface.h", "bdaiface_enums.h", "bdamedia.h", "bdatypes.h", "bemapiset.h", "bh.h", "bidispl.h", "bits.h", "bits1_5.h", "bits2_0.h", "bitscfg.h", "bitsmsg.h", "blberr.h", "bluetoothapis.h", "bthdef.h", "bthsdpdef.h", "bugcodes.h", "callobj.h", "cardmod.h", "casetup.h", "cchannel.h", "cderr.h", "cdoex.h", "cdoexerr.h", "cdoexm.h", "cdoexm_i.c", "cdoexstr.h", "cdoex_i.c", "cdonts.h", "cdosys.h", "cdosyserr.h", "cdosysstr.h", "cdosys_i.c", "celib.h", "certadm.h", "certbase.h", "certbcli.h", "certcli.h", "certenc.h", "certenroll.h", "certexit.h", "certif.h", "certmod.h", "certpol.h", "certreqd.h", "certsrv.h", "certview.h", "cfg.h", "cfgmgr32.h", "cguid.h", "chanmgr.h", "cierror.h", "clfs.h", "clfsmgmt.h", "clfsmgmtw32.h", "clfsw32.h", "cluadmex.h", "clusapi.h", "cluscfgguids.h", "cluscfgserver.h", "cluscfgwizard.h", "cmdtree.h", "cmnquery.h", "codecapi.h", "color.dlg", "colordlg.h", "comadmin.h", "combaseapi.h", "comcat.h", "comdef.h", "comdefsp.h", "comip.h", "comlite.h", "commapi.h", "commctrl.h", "commctrl.rh", "commdlg.h", "common.ver", "commoncontrols.h", "complex.h", "compobj.h", "compressapi.h", "compstui.h", "comsvcs.h", "comutil.h", "confpriv.h", "conio.h", "control.h", "cor.h", "corerror.h", "corhdr.h", "correg.h", "cpl.h", "cplext.h", "credssp.h", "crtdbg.h", "crtdefs.h", "cryptuiapi.h", "cryptxml.h", "cscapi.h", "cscobj.h", "ctfutb.h", "ctxtcall.h", "ctype.h", "custcntl.h", "d2d1.h", "d2d1effectauthor.h", "d2d1effecthelpers.h", "d2d1effects.h", "d2d1helper.h", "d2d1_1.h", "d2d1_1helper.h", "d2dbasetypes.h", "d2derr.h", "d3d.h", "d3d8.h", "d3d8caps.h", "d3d8types.h", "d3d9.h", "d3d9caps.h", "d3d9types.h", "d3d10.h", "d3d10.idl", "d3d10effect.h", "d3d10misc.h", "d3d10shader.h", "d3d10_1.h", "d3d10_1.idl", "d3d10_1shader.h", "d3d11.h", "d3d11.idl", "d3d11sdklayers.h", "d3d11sdklayers.idl", "d3d11shader.h", "d3d11_1.h", "d3d11_1.idl", "d3dcaps.h", "d3dcommon.h", "d3dcommon.idl", "d3dcompiler.h", "d3dhal.h", "d3drm.h", "d3drmdef.h", "d3drmobj.h", "d3dtypes.h", "d3dvec.inl", "d3dx9.h", "d3dx9anim.h", "d3dx9core.h", "d3dx9effect.h", "d3dx9math.h", "d3dx9math.inl", "d3dx9mesh.h", "d3dx9shader.h", "d3dx9shape.h", "d3dx9tex.h", "d3dx9xof.h", "daogetrw.h", "datapath.h", "datetimeapi.h", "davclnt.h", "dbdaoerr.h", "dbdaoid.h", "dbdaoint.h", "dbgautoattach.h", "dbgeng.h", "dbghelp.h", "dbgprop.h", "dbt.h", "dciddi.h", "dciman.h", "dcommon.h", "dcomp.h", "dcompanimation.h", "dcomptypes.h", "dde.h", "dde.rh", "ddeml.h", "ddk/acpiioct.h", "ddk/afilter.h", "ddk/amtvuids.h", "ddk/atm.h", "ddk/bdasup.h", "ddk/classpnp.h", "ddk/csq.h", "ddk/d3dhal.h", "ddk/d3dhalex.h", "ddk/d4drvif.h", "ddk/d4iface.h", "ddk/dderror.h", "ddk/dmusicks.h", "ddk/drivinit.h", "ddk/drmk.h", "ddk/dxapi.h", "ddk/fltsafe.h", "ddk/hidclass.h", "ddk/hubbusif.h", "ddk/ide.h", "ddk/ioaccess.h", "ddk/kbdmou.h", "ddk/mcd.h", "ddk/mce.h", "ddk/miniport.h", "ddk/minitape.h", "ddk/mountdev.h", "ddk/mountmgr.h", "ddk/msports.h", "ddk/ndis.h", "ddk/ndisguid.h", "ddk/ndistapi.h", "ddk/ndiswan.h", "ddk/netpnp.h", "ddk/ntagp.h", "ddk/ntddk.h", "ddk/ntddpcm.h", "ddk/ntddsnd.h", "ddk/ntifs.h", "ddk/ntimage.h", "ddk/ntnls.h", "ddk/ntpoapi.h", "ddk/ntstrsafe.h", "ddk/oprghdlr.h", "ddk/parallel.h", "ddk/pfhook.h", "ddk/poclass.h", "ddk/portcls.h", "ddk/punknown.h", "ddk/scsi.h", "ddk/scsiscan.h", "ddk/scsiwmi.h", "ddk/smbus.h", "ddk/srb.h", "ddk/stdunk.h", "ddk/storport.h", "ddk/strmini.h", "ddk/swenum.h", "ddk/tdikrnl.h", "ddk/tdistat.h", "ddk/upssvc.h", "ddk/usbbusif.h", "ddk/usbdlib.h", "ddk/usbdrivr.h", "ddk/usbkern.h", "ddk/usbprint.h", "ddk/usbprotocoldefs.h", "ddk/usbscan.h", "ddk/usbstorioctl.h", "ddk/video.h", "ddk/videoagp.h", "ddk/wdm.h", "ddk/wdmguid.h", "ddk/wmidata.h", "ddk/wmilib.h", "ddk/ws2san.h", "ddk/xfilter.h", "ddraw.h", "ddrawgdi.h", "ddrawi.h", "ddstream.h", "ddstream.idl", "debugapi.h", "delayimp.h", "devguid.h", "devicetopology.h", "devioctl.h", "devpkey.h", "devpropdef.h", "dhcpcsdk.h", "dhcpsapi.h", "dhcpssdk.h", "dhcpv6csdk.h", "dhtmldid.h", "dhtmled.h", "dhtmliid.h", "digitalv.h", "dimm.h", "dinput.h", "dir.h", "direct.h", "dirent.h", "diskguid.h", "dispatch.h", "dispdib.h", "dispex.h", "dlcapi.h", "dlgs.h", "dls1.h", "dls2.h", "dmdls.h", "dmemmgr.h", "dmerror.h", "dmksctrl.h", "dmo.h", "dmodshow.h", "dmodshow.idl", "dmoreg.h", "dmort.h", "dmplugin.h", "dmusbuff.h", "dmusicc.h", "dmusicf.h", "dmusici.h", "dmusics.h", "docobj.h", "docobjectservice.h", "documenttarget.h", "domdid.h", "dos.h", "downloadmgr.h", "dpaddr.h", "dpapi.h", "dpfilter.h", "dplay.h", "dplay8.h", "dplobby.h", "dplobby8.h", "dpnathlp.h", "driverspecs.h", "dsadmin.h", "dsclient.h", "dsconf.h", "dsdriver.h", "dsgetdc.h", "dshow.h", "dskquota.h", "dsound.h", "dsquery.h", "dsrole.h", "dssec.h", "dtchelp.h", "dvbsiparser.h", "dvdevcod.h", "dvdmedia.h", "dvec.h", "dvobj.h", "dwmapi.h", "dwrite.h", "dwrite_1.h", "dwrite_2.h", "dxdiag.h", "dxerr8.h", "dxerr9.h", "dxfile.h", "dxgi.h", "dxgi.idl", "dxgi1_2.h", "dxgi1_2.idl", "dxgiformat.h", "dxgitype.h", "dxtmpl.h", "dxva.h", "dxva2api.h", "dxvahd.h", "eapauthenticatoractiondefine.h", "eapauthenticatortypes.h", "eaphosterror.h", "eaphostpeerconfigapis.h", "eaphostpeertypes.h", "eapmethodauthenticatorapis.h", "eapmethodpeerapis.h", "eapmethodtypes.h", "eappapis.h", "eaptypes.h", "edevdefs.h", "eh.h", "ehstorapi.h", "elscore.h", "emostore.h", "emostore_i.c", "emptyvc.h", "endpointvolume.h", "errhandlingapi.h", "errno.h", "error.h", "errorrep.h", "errors.h", "esent.h", "evcode.h", "evcoll.h", "eventsys.h", "evntcons.h", "evntprov.h", "evntrace.h", "evr.h", "evr9.h", "exchform.h", "excpt.h", "exdisp.h", "exdispid.h", "fci.h", "fcntl.h", "fdi.h", "fenv.h", "fibersapi.h", "fileapi.h", "fileextd.h", "filehc.h", "fileopen.dlg", "filter.h", "filterr.h", "findtext.dlg", "float.h", "fltdefs.h", "fltuser.h", "fltuserstructures.h", "fltwinerror.h", "font.dlg", "fpieee.h", "fsrm.h", "fsrmenums.h", "fsrmerr.h", "fsrmpipeline.h", "fsrmquota.h", "fsrmreports.h", "fsrmscreen.h", "ftsiface.h", "ftw.h", "functiondiscoveryapi.h", "functiondiscoverycategories.h", "functiondiscoveryconstraints.h", "functiondiscoverykeys.h", "functiondiscoverykeys_devpkey.h", "functiondiscoverynotification.h", "fusion.h", "fvec.h", "fwpmtypes.h", "fwpmu.h", "fwptypes.h", "gb18030.h", "gdiplus.h", "gdiplus/gdiplus.h", "gdiplus/gdiplusbase.h", "gdiplus/gdiplusbrush.h", "gdiplus/gdipluscolor.h", "gdiplus/gdipluscolormatrix.h", "gdiplus/gdipluseffects.h", "gdiplus/gdiplusenums.h", "gdiplus/gdiplusflat.h", "gdiplus/gdiplusgpstubs.h", "gdiplus/gdiplusgraphics.h", "gdiplus/gdiplusheaders.h", "gdiplus/gdiplusimageattributes.h", "gdiplus/gdiplusimagecodec.h", "gdiplus/gdiplusimaging.h", "gdiplus/gdiplusimpl.h", "gdiplus/gdiplusinit.h", "gdiplus/gdipluslinecaps.h", "gdiplus/gdiplusmatrix.h", "gdiplus/gdiplusmem.h", "gdiplus/gdiplusmetafile.h", "gdiplus/gdiplusmetaheader.h", "gdiplus/gdipluspath.h", "gdiplus/gdipluspen.h", "gdiplus/gdipluspixelformats.h", "gdiplus/gdiplusstringformat.h", "gdiplus/gdiplustypes.h", "getopt.h", "gpedit.h", "gpio.h", "gpmgmt.h", "guiddef.h", "h323priv.h", "handleapi.h", "heapapi.h", "hidclass.h", "hidpi.h", "hidsdi.h", "hidusage.h", "highlevelmonitorconfigurationapi.h", "hlguids.h", "hliface.h", "hlink.h", "hostinfo.h", "hstring.h", "htiface.h", "htiframe.h", "htmlguid.h", "htmlhelp.h", "http.h", "httpext.h", "httpfilt.h", "httprequestid.h", "ia64reg.h", "iaccess.h", "iadmext.h", "iadmw.h", "iads.h", "icftypes.h", "icm.h", "icmpapi.h", "icmui.dlg", "icodecapi.h", "icrsint.h", "identitycommon.h", "identitystore.h", "idf.h", "idispids.h", "iedial.h", "ieeefp.h", "ieverp.h", "ifdef.h", "iiis.h", "iiisext.h", "iimgctx.h", "iiscnfg.h", "iisext_i.c", "iisrsta.h", "iketypes.h", "ilogobj.hxx", "imagehlp.h", "ime.h", "imessage.h", "imm.h", "in6addr.h", "inaddr.h", "indexsrv.h", "inetreg.h", "inetsdk.h", "infstr.h", "initguid.h", "initoid.h", "inputscope.h", "inspectable.h", "interlockedapi.h", "intrin.h", "intsafe.h", "intshcut.h", "inttypes.h", "invkprxy.h", "io.h", "ioapiset.h", "ioevent.h", "ipexport.h", "iphlpapi.h", "ipifcons.h", "ipinfoid.h", "ipmib.h", "ipmsp.h", "iprtrmib.h", "ipsectypes.h", "iptypes.h", "ipxconst.h", "ipxrip.h", "ipxrtdef.h", "ipxsap.h", "ipxtfflt.h", "iscsidsc.h", "isguids.h", "issper16.h", "issperr.h", "isysmon.h", "ivec.h", "iwamreg.h", "i_cryptasn1tls.h", "jobapi.h", "kcom.h", "knownfolders.h", "ks.h", "ksdebug.h", "ksguid.h", "ksmedia.h", "ksproxy.h", "ksuuids.h", "ktmtypes.h", "ktmw32.h", "kxia64.h", "l2cmn.h", "libgen.h", "libloaderapi.h", "limits.h", "lm.h", "lmaccess.h", "lmalert.h", "lmapibuf.h", "lmat.h", "lmaudit.h", "lmconfig.h", "lmcons.h", "lmdfs.h", "lmerr.h", "lmerrlog.h", "lmjoin.h", "lmmsg.h", "lmon.h", "lmremutl.h", "lmrepl.h", "lmserver.h", "lmshare.h", "lmsname.h", "lmstats.h", "lmsvc.h", "lmuse.h", "lmuseflg.h", "lmwksta.h", "loadperf.h", "locale.h", "locationapi.h", "lpmapi.h", "lzexpand.h", "madcapcl.h", "magnification.h", "mailmsgprops.h", "malloc.h", "manipulations.h", "mapi.h", "mapicode.h", "mapidbg.h", "mapidefs.h", "mapiform.h", "mapiguid.h", "mapihook.h", "mapinls.h", "mapioid.h", "mapispi.h", "mapitags.h", "mapiutil.h", "mapival.h", "mapiwin.h", "mapiwz.h", "mapix.h", "math.h", "mbctype.h", "mbstring.h", "mciavi.h", "mcx.h", "mdbrole.hxx", "mdcommsg.h", "mddefw.h", "mdhcp.h", "mdmsg.h", "mediaerr.h", "mediaobj.h", "mediaobj.idl", "medparam.h", "medparam.idl", "mem.h", "memory.h", "memoryapi.h", "mergemod.h", "mfapi.h", "mferror.h", "mfidl.h", "mfmp2dlna.h", "mfobjects.h", "mfplay.h", "mfreadwrite.h", "mftransform.h", "mgm.h", "mgmtapi.h",
                     "midles.h", "mimedisp.h", "mimeinfo.h", "minmax.h", "minwinbase.h", "minwindef.h", "mlang.h", "mmc.h", "mmcobj.h", "mmdeviceapi.h", "mmreg.h", "mmstream.h", "mmstream.idl", "mmsystem.h", "mobsync.h", "moniker.h", "mpeg2bits.h", "mpeg2data.h", "mpeg2psiparser.h", "mpeg2structs.h", "mprapi.h", "mprerror.h", "mq.h", "mqmail.h", "mqoai.h", "msacm.h", "msacmdlg.dlg", "msacmdlg.h", "msado15.h", "msasn1.h", "msber.h", "mscat.h", "mschapp.h", "msclus.h", "mscoree.h", "msctf.h", "msctfmonitorapi.h", "msdadc.h", "msdaguid.h", "msdaipp.h", "msdaipper.h", "msdaora.h", "msdaosp.h", "msdasc.h", "msdasql.h", "msdatsrc.h", "msdrm.h", "msdrmdefs.h", "msdshape.h", "msfs.h", "mshtmcid.h", "mshtmdid.h", "mshtmhst.h", "mshtml.h", "mshtmlc.h", "msi.h", "msidefs.h", "msimcntl.h", "msimcsdk.h", "msinkaut.h", "msinkaut_i.c", "msiquery.h", "msoav.h", "msopc.h", "msp.h", "mspab.h", "mspaddr.h", "mspbase.h", "mspcall.h", "mspcoll.h", "mspenum.h", "msplog.h", "mspst.h", "mspstrm.h", "mspterm.h", "mspthrd.h", "msptrmac.h", "msptrmar.h", "msptrmvc.h", "msputils.h", "msrdc.h", "msremote.h", "mssip.h", "msstkppg.h", "mstask.h", "mstcpip.h", "msterr.h", "mswsock.h", "msxml.h", "msxml2.h", "msxml2did.h", "msxmldid.h", "mtsadmin.h", "mtsadmin_i.c", "mtsevents.h", "mtsgrp.h", "mtx.h", "mtxadmin.h", "mtxadmin_i.c", "mtxattr.h", "mtxdm.h", "muiload.h", "multimon.h", "multinfo.h", "mxdc.h", "namedpipeapi.h", "namespaceapi.h", "napcertrelyingparty.h", "napcommon.h", "napenforcementclient.h", "napmanagement.h", "napmicrosoftvendorids.h", "napprotocol.h", "napservermanagement.h", "napsystemhealthagent.h", "napsystemhealthvalidator.h", "naptypes.h", "naputil.h", "nb30.h", "ncrypt.h", "ndattrib.h", "ndfapi.h", "ndhelper.h", "ndkinfo.h", "ndr64types.h", "ndrtypes.h", "netcon.h", "neterr.h", "netevent.h", "netioapi.h", "netlistmgr.h", "netmon.h", "netprov.h", "nettypes.h", "new.h", "newapis.h", "newdev.h", "nldef.h", "nmsupp.h", "npapi.h", "nsemail.h", "nspapi.h", "ntdd1394.h", "ntdd8042.h", "ntddbeep.h", "ntddcdrm.h", "ntddcdvd.h", "ntddchgr.h", "ntdddisk.h", "ntddft.h", "ntddkbd.h", "ntddmmc.h", "ntddmodm.h", "ntddmou.h", "ntddndis.h", "ntddpar.h", "ntddpsch.h", "ntddscsi.h", "ntddser.h", "ntddstor.h", "ntddtape.h", "ntddtdi.h", "ntddvdeo.h", "ntddvol.h", "ntdef.h", "ntdsapi.h", "ntdsbcli.h", "ntdsbmsg.h", "ntgdi.h", "ntiologc.h", "ntldap.h", "ntmsapi.h", "ntmsmli.h", "ntquery.h", "ntsdexts.h", "ntsecapi.h", "ntsecpkg.h", "ntstatus.h", "ntverp.h", "oaidl.h", "objbase.h", "objectarray.h", "objerror.h", "objidl.h", "objidlbase.h", "objsafe.h", "objsel.h", "ocidl.h", "ocmm.h", "odbcinst.h", "odbcss.h", "ole.h", "ole2.h", "ole2ver.h", "oleacc.h", "oleauto.h", "olectl.h", "olectlid.h", "oledb.h", "oledbdep.h", "oledberr.h", "oledbguid.h", "oledlg.dlg", "oledlg.h", "oleidl.h", "oletx2xa.h", "opmapi.h", "optary.h", "p2p.h", "packoff.h", "packon.h", "parser.h", "patchapi.h", "patchwiz.h", "pathcch.h", "pbt.h", "pchannel.h", "pciprop.h", "pcrt32.h", "pdh.h", "pdhmsg.h", "penwin.h", "perflib.h", "perhist.h", "persist.h", "pgobootrun.h", "physicalmonitorenumerationapi.h", "pla.h", "pnrpdef.h", "pnrpns.h", "poclass.h", "polarity.h", "poppack.h", "portabledeviceconnectapi.h", "portabledevicetypes.h", "powrprof.h", "prnasnot.h", "prnsetup.dlg", "prntfont.h", "process.h", "processenv.h", "processthreadsapi.h", "processtopologyapi.h", "profile.h", "profileapi.h", "profinfo.h", "propidl.h", "propkey.h", "propkeydef.h", "propsys.h", "propvarutil.h", "prsht.h", "psapi.h", "psdk_inc/intrin-impl.h", "psdk_inc/_dbg_LOAD_IMAGE.h", "psdk_inc/_dbg_common.h", "psdk_inc/_fd_types.h", "psdk_inc/_ip_mreq1.h", "psdk_inc/_ip_types.h", "psdk_inc/_pop_BOOL.h", "psdk_inc/_push_BOOL.h", "psdk_inc/_socket_types.h", "psdk_inc/_varenum.h", "psdk_inc/_ws1_undef.h", "psdk_inc/_wsadata.h", "psdk_inc/_wsa_errnos.h", "psdk_inc/_xmitfile.h", "pshpack1.h", "pshpack2.h", "pshpack4.h", "pshpack8.h", "pshpck16.h", "pstore.h", "pthread.h", "pthread_compat.h", "pthread_signal.h", "pthread_time.h", "pthread_unistd.h", "qedit.h", "qedit.idl", "qmgr.h", "qnetwork.h", "qnetwork.idl", "qos.h", "qos2.h", "qosname.h", "qospol.h", "qossp.h", "ras.h", "rasdlg.h", "raseapif.h", "raserror.h", "rassapi.h", "rasshost.h", "ratings.h", "rdpencomapi.h", "realtimeapiset.h", "reason.h", "recguids.h", "reconcil.h", "regbag.h", "regstr.h", "rend.h", "resapi.h", "restartmanager.h", "richedit.h", "richole.h", "rkeysvcc.h", "rnderr.h", "roapi.h", "routprot.h", "rpc.h", "rpcasync.h", "rpcdce.h", "rpcdcep.h", "rpcndr.h", "rpcnsi.h", "rpcnsip.h", "rpcnterr.h", "rpcproxy.h", "rpcsal.h", "rpcssl.h", "rrascfg.h", "rtcapi.h", "rtccore.h", "rtcerr.h", "rtinfo.h", "rtm.h", "rtmv2.h", "rtutils.h", "sal.h", "sapi.h", "sapi51.h", "sapi53.h", "sapi54.h", "sas.h", "sbe.h", "scarddat.h", "scarderr.h", "scardmgr.h", "scardsrv.h", "scardssp.h", "scardssp_i.c", "scardssp_p.c", "scesvc.h", "schannel.h", "sched.h", "schedule.h", "schemadef.h", "schnlsp.h", "scode.h", "scrnsave.h", "scrptids.h", "sddl.h", "sdkddkver.h", "sdks/_mingw_ddk.h", "sdks/_mingw_directx.h", "sdoias.h", "sdpblb.h", "sdperr.h", "search.h", "secext.h", "security.h", "securityappcontainer.h", "securitybaseapi.h", "sec_api/conio_s.h", "sec_api/crtdbg_s.h", "sec_api/mbstring_s.h", "sec_api/search_s.h", "sec_api/stdio_s.h", "sec_api/stdlib_s.h", "sec_api/stralign_s.h", "sec_api/string_s.h", "sec_api/sys/timeb_s.h", "sec_api/tchar_s.h", "sec_api/wchar_s.h", "sehmap.h", "semaphore.h", "sens.h", "sensapi.h", "sensevts.h", "sensors.h", "sensorsapi.h", "servprov.h", "setjmp.h", "setjmpex.h", "setupapi.h", "sfc.h", "shappmgr.h", "share.h", "shdeprecated.h", "shdispid.h", "shellapi.h", "sherrors.h", "shfolder.h", "shldisp.h", "shlguid.h", "shlobj.h", "shlwapi.h", "shobjidl.h", "shtypes.h", "signal.h", "simpdata.h", "simpdc.h", "sipbase.h", "sisbkup.h", "slerror.h", "slpublic.h", "smpab.h", "smpms.h", "smpxp.h", "smtpguid.h", "smx.h", "snmp.h", "softpub.h", "specstrings.h", "sperror.h", "sphelper.h", "sporder.h", "sql.h", "sqlext.h", "sqloledb.h", "sqltypes.h", "sqlucode.h", "sql_1.h", "srrestoreptapi.h", "srv.h", "sspguid.h", "sspi.h", "sspserr.h", "sspsidl.h", "stdarg.h", "stddef.h", "stdexcpt.h", "stdint.h", "stdio.h", "stdlib.h", "sti.h", "stierr.h", "stireg.h", "stllock.h", "stm.h", "storage.h", "storduid.h", "storprop.h", "stralign.h", "string.h", "stringapiset.h", "strings.h", "strmif.h", "strsafe.h", "structuredquerycondition.h", "subauth.h", "subsmgr.h", "svcguid.h", "svrapi.h", "swprintf.inl", "synchapi.h", "sysinfoapi.h", "syslimits.h", "systemtopologyapi.h", "sys/cdefs.h", "sys/fcntl.h", "sys/file.h", "sys/locking.h", "sys/param.h", "sys/stat.h", "sys/time.h", "sys/timeb.h", "sys/types.h", "sys/unistd.h", "sys/utime.h", "t2embapi.h", "tabflicks.h", "tapi.h", "tapi3.h", "tapi3cc.h", "tapi3ds.h", "tapi3err.h", "tapi3if.h", "taskschd.h", "tbs.h", "tcerror.h", "tcguid.h", "tchar.h", "tcpestats.h", "tcpmib.h", "tdh.h", "tdi.h", "tdiinfo.h", "termmgr.h", "textserv.h", "textstor.h", "threadpoolapiset.h", "threadpoollegacyapiset.h", "time.h", "timeprov.h", "timezoneapi.h", "tlbref.h", "tlhelp32.h", "tlogstg.h", "tmschema.h", "tnef.h", "tom.h", "tpcshrd.h", "traffic.h", "transact.h", "triedcid.h", "triediid.h", "triedit.h", "tsattrs.h", "tspi.h", "tssbx.h", "tsuserex.h", "tsuserex_i.c", "tuner.h", "tvout.h", "txcoord.h", "txctx.h", "txdtc.h", "txfw32.h", "typeinfo.h", "uastrfnc.h", "uchar.h", "udpmib.h", "uiautomation.h", "uiautomationclient.h", "uiautomationcore.h", "uiautomationcoreapi.h", "uiviewsettingsinterop.h", "umx.h", "unistd.h", "unknown.h", "unknwn.h", "unknwnbase.h", "urlhist.h", "urlmon.h", "usb.h", "usb100.h", "usb200.h", "usbcamdi.h", "usbdi.h", "usbioctl.h", "usbiodef.h", "usbprint.h", "usbrpmif.h", "usbscan.h", "usbspec.h", "usbuser.h", "userenv.h", "usp10.h", "utilapiset.h", "utime.h", "uuids.h", "uxtheme.h", "vadefs.h", "varargs.h", "vcr.h", "vdmdbg.h", "vds.h", "vdslun.h", "verinfo.ver", "versionhelpers.h", "vfw.h", "vfwmsgs.h", "virtdisk.h", "vmr9.h", "vmr9.idl", "vsadmin.h", "vsbackup.h", "vsmgmt.h", "vsprov.h", "vss.h", "vsstyle.h", "vssym32.h", "vswriter.h", "w32api.h", "wab.h", "wabapi.h", "wabcode.h", "wabdefs.h", "wabiab.h", "wabmem.h", "wabnot.h", "wabtags.h", "wabutil.h", "wbemads.h", "wbemcli.h", "wbemdisp.h", "wbemidl.h", "wbemprov.h", "wbemtran.h", "wchar.h", "wcmconfig.h", "wcsplugin.h", "wct.h", "wctype.h", "wdsbp.h", "wdsclientapi.h", "wdspxe.h", "wdstci.h", "wdstpdi.h", "wdstptmgmt.h", "werapi.h", "wfext.h", "wia.h", "wiadef.h", "wiadevd.h", "wiavideo.h", "winable.h", "winapifamily.h", "winbase.h", "winber.h", "wincodec.h", "wincon.h", "wincred.h", "wincrypt.h", "winddi.h", "winddiui.h", "windef.h", "windns.h", "windot11.h", "windows.foundation.h", "windows.h", "windows.security.cryptography.h", "windows.storage.h", "windows.storage.streams.h", "windows.system.threading.h", "windowsx.h", "windowsx.h16", "winefs.h", "winerror.h", "winevt.h", "wingdi.h", "winhttp.h", "wininet.h", "winineti.h", "winioctl.h", "winldap.h", "winnetwk.h", "winnls.h", "winnls32.h", "winnt.h", "winnt.rh", "winperf.h", "winreg.h", "winresrc.h", "winsafer.h", "winsatcominterfacei.h", "winscard.h", "winsdkver.h", "winsmcrd.h", "winsnmp.h", "winsock.h", "winsock2.h", "winsplp.h", "winspool.h", "winstring.h", "winsvc.h", "winsxs.h", "winsync.h", "winternl.h", "wintrust.h", "winusb.h", "winusbio.h", "winuser.h", "winuser.rh", "winver.h", "winwlx.h", "wlanapi.h", "wlanihvtypes.h", "wlantypes.h", "wmcodecdsp.h", "wmcontainer.h", "wmiatlprov.h", "wmistr.h", "wmiutils.h", "wmsbuffer.h", "wmsdkidl.h", "wnnc.h", "wow64apiset.h", "wownt16.h", "wownt32.h", "wpapi.h", "wpapimsg.h", "wpcapi.h", "wpcevent.h", "wpcrsmsg.h", "wpftpmsg.h", "wppstmsg.h", "wpspihlp.h", "wptypes.h", "wpwizmsg.h", "wrl.h", "wrl/client.h", "wrl/internal.h", "wrl/module.h", "wrl/wrappers/corewrappers.h", "ws2atm.h", "ws2bth.h", "ws2def.h", "ws2dnet.h", "ws2ipdef.h", "ws2spi.h", "ws2tcpip.h", "wsdapi.h", "wsdattachment.h", "wsdbase.h", "wsdclient.h", "wsddisco.h", "wsdhost.h", "wsdtypes.h", "wsdutil.h", "wsdxml.h", "wsdxmldom.h", "wshisotp.h", "wsipv6ok.h", "wsipx.h", "wsman.h", "wsmandisp.h", "wsnetbs.h", "wsnwlink.h", "wspiapi.h", "wsrm.h", "wsvns.h", "wtsapi32.h", "wtypes.h", "wtypesbase.h", "xa.h", "xcmc.h", "xcmcext.h", "xcmcmsx2.h", "xcmcmsxt.h", "xenroll.h", "xinput.h", "xlocinfo.h", "xmath.h", "xmldomdid.h", "xmldsodid.h", "xmllite.h", "xmltrnsf.h", "xolehlp.h", "xpsdigitalsignature.h", "xpsobjectmodel.h", "xpsobjectmodel_1.h", "xpsprint.h", "xpsrassvc.h", "ymath.h", "yvals.h", "zmouse.h", "_bsd_types.h", "_cygwin.h", "_dbdao.h", "_mingw.h", "_mingw_dxhelper.h", "_mingw_mac.h", "_mingw_off_t.h", "_mingw_print_pop.h", "_mingw_print_push.h", "_mingw_secapi.h", "_mingw_stat64.h", "_mingw_stdarg.h", "_mingw_unicode.h", "_timeval.h")

    flag_dict = {}  # Map include files to flags
    global_flag_dict = {}  # For -I flags, to not overwrite the flags for include files in flag_dict

    # Flags for standard includes must come before the skiplist check below.

    # Add -pthread for thread-related includes from stdlib (POSIX threads)
    # The list of includes to be checked for here is from:
    # http://en.cppreference.com/w/cpp/thread
    for include in includes:
        if include.strip() in ("condition_variable", "future", "mutex", "new", "pthread.h", "thread"):
            new_flags = "-pthread -lpthread"
            if include in flag_dict:
                flag_dict[include] += " " + new_flags
            else:
                flag_dict[include] = new_flags

    # Filter out skipped includes, and includes in LOCAL_INCLUDE_PATHS
    filtered_includes = []
    for include in includes:
        if include in skiplist:
            continue
        if win64 and (include in win64skiplist):
            continue
        found = False
        for local_include_path in LOCAL_INCLUDE_PATHS:
            if os.path.exists(os.path.join(local_include_path, include)):
                found = True
                break
        if not found:
            filtered_includes.append(include)
    includes = filtered_includes

    # Check for installed frameworks in /Library/Frameworks
    if platform.system() == "Darwin":
        # on macOS, prefer not to use pkg-config
        for include in includes:
            first_word = include
            if os.path.sep in include:
                first_word = include.split(os.path.sep)[0].strip().lower()
            if os.path.exists("/Library/Frameworks/" + first_word + ".framework"):
                # Found it!
                new_flags = ""
                if "/usr/local/include" not in compiler_includes:
                    new_flags = "-I/usr/local/include "
                new_flags += "-F/Library/Frameworks -framework " + first_word
                if include in flag_dict:
                    flag_dict[include] += " " + new_flags
                else:
                    flag_dict[include] = new_flags

    # If the include exists in one of the include directories: what is the first word, in lowercase?
    if not win64:
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                if os.path.exists(os.path.join(system_include_dir, include)):
                    # Add the include directory as an -I flag if the include file was found
                    if include in flag_dict:
                        global_flag_dict[include] += " -I" + system_include_dir
                    else:
                        global_flag_dict[include] = "-I" + system_include_dir
                    # If pkg-config exists, add additional flags
                    if has_pkg_config:
                        # Add flags from pkg-config, if available for the first word of the include
                        first_word = include.lower()
                        if os.path.sep in include:
                            first_word = include.split(os.path.sep)[0].lower()
                        cmd = "pkg-config --cflags --libs " + first_word + " 2>/dev/null"
                        try:
                            new_flags = os.popen2(cmd)[1].read().strip()
                        except OSError:
                            new_flags = ""
                        if new_flags:
                            if include in flag_dict:
                                flag_dict[include] += " " + new_flags
                            else:
                                flag_dict[include] = new_flags

    # Search the x86_64-w64-mingw32 path
    if win64:
        mingw_include_dir = "/usr/x86_64-w64-mingw32/include"
        for include in includes:
            if include in flag_dict:
                continue
            if os.path.exists(os.path.join(mingw_include_dir, include)):
                # Add the include directory as an -I flag if the include file was found
                if include in global_flag_dict:
                    global_flag_dict[include] += " -I" + mingw_include_dir
                else:
                    global_flag_dict[include] = "-I" + mingw_include_dir

    # NetBSD include path
    if os.path.exists("/usr/pkg/include"):
        netbsd_include_dir = "/usr/pkg/include"
        for include in includes:
            if include in flag_dict:
                continue
            if os.path.exists(os.path.join(netbsd_include_dir, include)):
                # Add the include directory as an -I flag if the include file was found
                if include in global_flag_dict:
                    global_flag_dict[include] += " -I" + netbsd_include_dir
                else:
                    global_flag_dict[include] = "-I" + netbsd_include_dir

    # OpenBSD include path (and maybe other systems too)
    if os.path.exists("/usr/local/include"):
        openbsd_include_dir = "/usr/local/include"
        for include in includes:
            if include in flag_dict:
                continue
            if os.path.exists(os.path.join(openbsd_include_dir, include)):
                # Add the include directory as an -I flag if the include file was found
                if include in global_flag_dict:
                    global_flag_dict[include] += " -I" + openbsd_include_dir
                else:
                    global_flag_dict[include] = "-I" + openbsd_include_dir

    # If there are now missing build flags, and pkg-config is not in the path, it's a problem
    missing_includes = [
        include for include in includes if include not in flag_dict and include not in global_flag_dict]
    if missing_includes and not has_pkg_config:
        print("\nerror: missing in PATH: pkg-config")
        exit(1)

    # Guess g++ or gcc, only for running -dumpmachine for machine identification
    if not (cxx and which(cxx)):
        if which("g++"):
            cxx = "g++"
        elif which("gcc"):
            cxx = "gcc"
        elif which("g++9"):
            cxx = "g++9"
        elif which("g++-9"):
            cxx = "g++-9"
        elif which("g++8"):
            cxx = "g++8"
        elif which("g++-8"):
            cxx = "g++-8"
        elif which("g++7"):
            cxx = "g++7"
        elif which("g++-7"):
            cxx = "g++-7"
        elif which("eg++"):
            cxx = "eg++"

    # Using the include_lines, find the correct CFLAGS on Debian/Ubuntu
    if has_pkg_config and exe("/usr/bin/dpkg-query") and not exe("/usr/bin/pacman"):
        has_package_manager = True
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                include_path = os.path.join(system_include_dir, include)
                new_flags = deb_include_path_to_cxxflags(include_path, cxx)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags
        # Try the same with dpkg-query, but now using find to search deeper in system_include_dir
        for include in includes:
            if include in flag_dict:
                continue
            # Search system_include_dir
            for system_include_dir in system_include_dirs:
                cmd = '/usr/bin/find ' + system_include_dir + ' -maxdepth 3 -type f -wholename "*' + \
                    include + '" | /usr/bin/sort -V | /usr/bin/tail -1'
                try:
                    include_path = os.popen2(cmd)[1].read().strip()
                except OSError:
                    include_path = ""
                if include_path:
                    new_flags = deb_include_path_to_cxxflags(include_path, cxx)
                    if new_flags:
                        if include in flag_dict:
                            flag_dict[include] += " " + new_flags
                        else:
                            flag_dict[include] = new_flags

    # Using the include_lines, find the correct CFLAGS on Arch Linux
    if has_pkg_config and exe("/usr/bin/pacman"):
        has_package_manager = True
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                include_path = os.path.join(system_include_dir, include)
                # if ("/wine/" in include_path) and not win64:
                #    continue
                new_flags = arch_include_path_to_cxxflags(include_path)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags
            # Try the same with pacman, but now using find to search deeper in the system include dir
            if include in flag_dict:
                continue
            # Search the system include dir
            for system_include_dir in system_include_dirs:
                cmd = '/usr/bin/find ' + system_include_dir + ' -maxdepth 3 -type f -wholename "*' + \
                    include + '" | /usr/bin/sort -V | /usr/bin/tail -1'
                try:
                    include_path = os.popen2(cmd)[1].read().strip()
                except OSError:
                    include_path = ""
                if include_path:
                    new_flags = arch_include_path_to_cxxflags(include_path)
                    if new_flags:
                        if include in flag_dict:
                            flag_dict[include] += " " + new_flags
                        else:
                            flag_dict[include] = new_flags

    # Using the include_lines, find the correct CFLAGS on FreeBSD
    if has_pkg_config and exe("/usr/sbin/pkg"):
        has_package_manager = True
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                include_path = os.path.join(system_include_dir, include)
                new_flags = freebsd_include_path_to_cxxflags(include_path)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags
            # Try the same, but now using find to search deeper in system_include_dir
            if include in flag_dict:
                continue
            # Search system_include_dir
            for system_include_dir in system_include_dirs:
                cmd = '/usr/bin/find ' + system_include_dir + ' -maxdepth 3 -type f -wholename "*' + \
                    include + '" | /usr/bin/sort -V | /usr/bin/tail -1'
                try:
                    include_path = os.popen2(cmd)[1].read().strip()
                except OSError:
                    include_path = ""
                if include_path:
                    new_flags = freebsd_include_path_to_cxxflags(include_path)
                    if new_flags:
                        if include in flag_dict:
                            flag_dict[include] += " " + new_flags
                        else:
                            flag_dict[include] = new_flags

    # Using the include_lines, find the correct CFLAGS on OpenBSD
    if has_pkg_config and exe("/usr/sbin/pkg_info"):
        has_package_manager = True
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                include_path = os.path.join(system_include_dir, include)
                new_flags = openbsd_include_path_to_cxxflags(include_path)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags
            # Try the same, but now using find to search deeper in system_include_dir
            if include in flag_dict:
                continue
            # Search system_include_dir
            for system_include_dir in system_include_dirs:
                cmd = '/usr/bin/find ' + system_include_dir + ' -maxdepth 3 -type f -path "*' + \
                    include + '" | /usr/bin/sort -V | /usr/bin/tail -1'
                try:
                    include_path = os.popen2(cmd)[1].read().strip()
                except OSError:
                    include_path = ""
                include_path = os.path.dirname(include_path)
                if include_path and os.path.exists(include_path):
                    new_flags = openbsd_include_path_to_cxxflags(include_path)
                    if new_flags:
                        if include in flag_dict:
                            flag_dict[include] += " " + new_flags
                        else:
                            flag_dict[include] = new_flags

    # Using the include_lines, find the correct CFLAGS on macOS with Homebrew and pkg-config installed
    if has_pkg_config and which("brew"):
        has_package_manager = True
        for include in includes:
            if include in flag_dict:
                continue
            # Homebrew does not support finding the package that owns a file, search /usr/local/include instead
            for system_include_dir in system_include_dirs:
                cmd = 'find -s -L ' + system_include_dir + ' -type f -wholename "*' + include + '" -maxdepth 4 | tail -1'
                try:
                    include_path = os.popen2(cmd)[1].read().strip()
                except OSError:
                    include_path = ""
                if not include_path:
                    # Could not find the include file in the system include dir, try searching /usr/local/Cellar for frameworks, and then headers
                    # This is much faster than searching for the header file directly, and it makes
                    # sense to look for the latest framework version before searching all of them.
                    cmd = 'find /usr/local/Cellar/ -name Frameworks -type d -maxdepth 3 | sort -V'
                    try:
                        framework_dirs = os.popen2(cmd)[1].read().strip().split(os.linesep)
                    except OSError:
                        framework_dirs = []
                    # If directories named "Frameworks" were found, sort them by version number and then search
                    # the directories of the ones with the highest version numbers for the include file
                    if framework_dirs:
                        # Collect the frameworks path in a dictionary, indexed by the part of the path with a framework name
                        framework_dict = {}
                        for framework_dir in framework_dirs:
                            path_components = framework_dir.split(os.path.sep)
                            if len(path_components) >= 5:
                                framework_dict[path_components[5]] = os.path.normpath(framework_dir)
                        # Loop over the framework directories belonging to the latest versions of the frameworks
                        # and look for the include file in question:
                        for framework_dir in framework_dict.values():
                            cmd = 'find -L "' + framework_dir + '" -type f -maxdepth 4 -name "' + include + '" | tail -1'
                            try:
                                include_path = os.popen2(cmd)[1].read().strip()
                            except OSError:
                                include_path = ""
                            if include_path:
                                # Now use the existing function for getting build flags from a found include file
                                new_flags = brew_include_path_to_cxxflags(include_path)
                                if new_flags:
                                    if include in flag_dict:
                                        flag_dict[include] += " " + new_flags
                                    else:
                                        flag_dict[include] = new_flags
                else:
                    new_flags = brew_include_path_to_cxxflags(include_path)
                    if new_flags:
                        if include in flag_dict:
                            flag_dict[include] += " " + new_flags
                        else:
                            flag_dict[include] = new_flags

    # Using the include_lines, try to guess the CFLAGS on a generic Linux distro
    if not has_package_manager:
        for include in includes:
            if include in flag_dict:
                continue
            for system_include_dir in system_include_dirs:
                include_path = os.path.join(system_include_dir, include)
                new_flags = generic_include_path_to_cxxflags(include_path)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags
        # For NetBSD
        if os.path.exists("/usr/pkg/include"):
            for include in includes:
                if include in flag_dict:
                    continue
                include_path = os.path.join("/usr/pkg/include", include)
                new_flags = generic_include_path_to_cxxflags(include_path)
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags

    # Special cases - additional build flags that should be reported as bugs and added to the ".pc" files that comes with libraries.
    # This must come last.
    for include in includes:

        # SFML on macOS, add OpenGL and if clang/zapcc, add -stdlib=libc++
        if include.split(os.path.sep)[0].strip().lower() == "sfml":
            new_flags = ""
            # Check if the macOS Frameworks path exists
            if os.path.exists("/Library/Frameworks") and not win64:
                # Found it, add the OpenGL framework as well
                new_flags = ""
                if "/usr/local/include" not in compiler_includes:
                    new_flags = "-I/usr/local/include "
                new_flags += "-F/Library/Frameworks -framework OpenGL"
                if include in flag_dict:
                    flag_dict[include] += " " + new_flags
                else:
                    flag_dict[include] = new_flags
                # if clang is set, add "-stdlib=libc++" when using SFML, on macOS
                if int(ARGUMENTS.get('clang', 0)) or int(ARGUMENTS.get('zap', 0)):
                    if include in flag_dict:
                        flag_dict[include] += " -stdlib=libc++"
                    else:
                        flag_dict[include] = " -stdlib=libc++"
                else:
                    # SFML is likely to fail with g++ on macOS, unfortunately
                    # If clang has not been specified, check CXX and give a warning
                    if cxx and cxx.startswith("g"):
                        print("WARNING: Compiling an application that uses SFML may require clang. Try: cxx rebuild clang=1")
            elif win64:
                new_flags = "-lopengl32"
                if include in flag_dict:
                    flag_dict[include] += " " + new_flags
                else:
                    flag_dict[include] = new_flags
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs gl 2>/dev/null"
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        flag_dict[include] += " " + new_flags
                    else:
                        flag_dict[include] = new_flags

        # If one of the includes just mention something with OpenGL, or GLUT, add build flags for OpenGL
        if ("opengl" in include.lower()) or include.startswith("GL/") or include.startswith("GLUT/"):
            # Also check if "glu" is mentioned in the sourcefile, since we'll also have to link with glu then
            also_glu = bool([line for line in source_lines if "glu" in line])
            new_flags = ""
            # Check if the macOS Frameworks path exists
            if os.path.exists("/Library/Frameworks") and not win64:
                # Found it, add the OpenGL framework as well
                new_flags = ""
                if "/usr/local/include" not in compiler_includes:
                    new_flags = "-I/usr/local/include "
                new_flags += "-F/Library/Frameworks -framework OpenGL"
                if also_glu:
                    new_flags += " -framework GLUT"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            elif win64:
                new_flags = "-lopengl32"
                if also_glu:
                    new_flags += " -lglu32"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs gl 2>/dev/null"
                if also_glu:
                    cmd = cmd.replace(" gl ", " gl glu ")
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        if new_flags not in flag_dict[include]:
                            flag_dict[include] += " " + new_flags
                    elif new_flags not in flag_dict.values():
                        flag_dict[include] = new_flags
            else:
                # if the libGL library is in /usr/lib, /usr/lib/x86_64-linux-gnu, /usr/local/lib or /usr/pkg/lib, link with that
                for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/pkg/lib"]:
                    if os.path.exists(os.path.join(libpath, "libGL.so")):
                        new_flags = "-lGL"
                        if also_glu:
                            new_flags += " -lGLU"
                        if include in flag_dict:
                            if new_flags not in flag_dict[include]:
                                flag_dict[include] += " " + new_flags
                        elif new_flags not in flag_dict.values():
                            flag_dict[include] = new_flags
                        break

        # If one of the includes just mention something with OpenAL, add build flags for OpenAL
        # AL/alc.h, OpenAL/OpenAL.h, OpenAL.h and OpenAL/al.h should all be detected.
        if include.startswith("AL/") or include.startswith("OpenAL") or "/al.h" in include:
            new_flags = ""
            # Check if the macOS Frameworks path exists
            if os.path.exists("/System/Library/Frameworks") and not win64:
                # Found it, add the OpenAL framework as well
                new_flags = ""
                if "/System/Library/Frameworks/OpenAL.framework/Headers" not in compiler_includes:
                    new_flags += "-I/System/Library/Frameworks/OpenAL.framework/Headers "
                if "-framework OpenAL" not in new_flags:
                    new_flags += "-F/System/Library/Frameworks -framework OpenAL"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            elif win64:
                new_flags = "-lopenal32"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs openal 2>/dev/null"
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        if new_flags not in flag_dict[include]:
                            flag_dict[include] += " " + new_flags
                    elif new_flags not in flag_dict.values():
                        flag_dict[include] = new_flags
            else:
                # if the libopenal library is in /usr/lib, /usr/lib/x86_64-linux-gnu, /usr/local/lib or /usr/pkg/lib, link with that
                for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/pkg/lib"]:
                    if os.path.exists(os.path.join(libpath, "libopenal.so")):
                        new_flags = "-lopenal"
                        if include in flag_dict:
                            if new_flags not in flag_dict[include]:
                                flag_dict[include] += " " + new_flags
                        elif new_flags not in flag_dict.values():
                            flag_dict[include] = new_flags
                        break

        # If one of the includes mentions "SDL2/SDL_*", add flags for "SDL2_*"
        if include.startswith("SDL2/SDL_"):
            word = "SDL2_" + include[9:].split(".")[0]
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs " + word + " 2>/dev/null"
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        if new_flags not in flag_dict[include]:
                            flag_dict[include] += " " + new_flags
                    elif new_flags not in flag_dict.values():
                        flag_dict[include] = new_flags
            else:
                # if the SDL2_* library is in /usr/lib, /usr/lib/x86_64-linux-gnu, /usr/local/lib or /usr/pkg/lib, link with that
                for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/pkg/lib"]:
                    if os.path.exists(os.path.join(libpath, "lib" + word + ".so")):
                        new_flags = "-l" + word
                        if include in flag_dict:
                            if new_flags not in flag_dict[include]:
                                flag_dict[include] += " " + new_flags
                        elif new_flags not in flag_dict.values():
                            flag_dict[include] = new_flags
                        break

        # If one of the includes just mention GLUT, add flags for GLUT or glu
        if include.startswith("GLUT/") or include.endswith("/glut.h"):
            new_flags = ""
            # Check if the macOS Frameworks path exists
            if os.path.exists("/Library/Frameworks") and not win64:
                # Found it, add the OpenGL framework as well
                new_flags = ""
                if "/usr/local/include" not in compiler_includes:
                    new_flags = "-I/usr/local/include "
                new_flags += "-F/Library/Frameworks -framework GLUT"
                if not int(ARGUMENTS.get('strict', 0)):  # if not strict=1
                    new_flags += " -Wno-deprecated-declarations"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            elif win64:
                new_flags = "-lglu32"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            else:
                # if the libglut library is in /usr/lib, /usr/lib/x86_64-linux-gnu, /usr/local/lib or
                # /usr/X11R7/lib, /usr/lib + machine_name, or /usr/pkg/lib; link with that
                machine_name = ""
                if cxx and which(cxx):
                    machine_name = os.popen2(cxx + " -dumpmachine")[1].read().strip()
                for libpath in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/local/lib", "/usr/X11R7/lib", "/usr/lib/" + machine_name, "/usr/pkg/lib"]:
                    if os.path.exists(os.path.join(libpath, "libglut.so")):
                        new_flags = "-lglut"  # Only configuration required for ie. freeglut
                        if include in flag_dict:
                            if new_flags not in flag_dict[include]:
                                flag_dict[include] += " " + new_flags
                        elif new_flags not in flag_dict.values():
                            flag_dict[include] = new_flags
                        break
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs glu 2>/dev/null"
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        if new_flags not in flag_dict[include]:
                            flag_dict[include] += " " + new_flags
                    elif new_flags not in flag_dict.values():
                        flag_dict[include] = new_flags
                else:
                    # Try pkg-config with freeglut and glut first. Needed on NetBSD.
                    cmd = "pkg-config --cflags --libs freeglut glut 2>/dev/null"
                    try:
                        new_flags = os.popen2(cmd)[1].read().strip()
                    except OSError:
                        new_flags = ""
                    if new_flags:
                        if include in flag_dict:
                            if new_flags not in flag_dict[include]:
                                flag_dict[include] += " " + new_flags
                        elif new_flags not in flag_dict.values():
                            flag_dict[include] = new_flags
                    else:
                        # Try pkg-config with just freeglut
                        cmd = "pkg-config --cflags --libs freeglut 2>/dev/null"
                        try:
                            new_flags = os.popen2(cmd)[1].read().strip()
                        except OSError:
                            new_flags = ""
                        if new_flags:
                            if include in flag_dict:
                                if new_flags not in flag_dict[include]:
                                    flag_dict[include] += " " + new_flags
                            elif new_flags not in flag_dict.values():
                                flag_dict[include] = new_flags

        # If one of the includes mention GLEW, add flags for GLEW
        if include.endswith("/glew.h"):
            new_flags = ""
            # Check if the macOS Frameworks path exists
            if win64:
                new_flags = "-lglew32"
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags
            if has_pkg_config:
                # Try pkg-config
                cmd = "pkg-config --cflags --libs glew 2>/dev/null"
                try:
                    new_flags = os.popen2(cmd)[1].read().strip()
                except OSError:
                    new_flags = ""
                if new_flags:
                    if include in flag_dict:
                        if new_flags not in flag_dict[include]:
                            flag_dict[include] += " " + new_flags
                    elif new_flags not in flag_dict.values():
                        flag_dict[include] = new_flags

        if include.startswith("Q"):
            for system_include_dir in system_include_dirs:
                qt_include_dir = os.path.join(system_include_dir, "qt")
                new_flags = ""
                if not int(ARGUMENTS.get('strict', 0)):  # if not strict=1
                    # These warnings kick in for the Qt5 include files themselves
                    new_flags += "-Wno-class-memaccess -Wno-pedantic"
                if os.path.exists(qt_include_dir):
                    if new_flags:
                        new_flags += " "
                    new_flags += "-I" + qt_include_dir
                if include in flag_dict:
                    if new_flags not in flag_dict[include]:
                        flag_dict[include] += " " + new_flags
                elif new_flags not in flag_dict.values():
                    flag_dict[include] = new_flags

        if include.startswith("glm/"):
            new_flags = ""
            if not int(ARGUMENTS.get('strict', 0)):  # if not strict=1
                # These warnings kick in for the glm include files themselves
                new_flags += "-Wno-shadow"
            if include in flag_dict:
                if new_flags not in flag_dict[include]:
                    flag_dict[include] += " " + new_flags
            elif new_flags not in flag_dict.values():
                flag_dict[include] = new_flags

    # List includes that were not found. "linux" is sometimes replaced with "1", which may cause issues.
    missing_includes = [
        include for include in includes if include not in flag_dict and include not in global_flag_dict and not include.startswith("1/")]

    if missing_includes:
        hints(missing_includes)
        # If sloppy is set, just give a warning
        if int(ARGUMENTS.get('sloppy', 0)):
            print("WARNING: missing include: {}".format(missing_includes[0]))
        else:
            # May recommend a package to install and then exit
            if exe("/usr/sbin/pkg"):  # FreeBSD
                for missing_include in missing_includes:
                    freebsd_recommend_package(missing_include)
            elif which("dpkg"):  # Debian / Ubuntu
                for missing_include in missing_includes:
                    deb_recommend_package(missing_include)
            elif which("pacman"):  # Arch
                for missing_include in missing_includes:
                    arch_recommend_package(missing_include)
            print("error: missing include: {}".format(missing_includes[0]))
            exit(1)
    else:
        if 'run' not in ARGUMENTS:
            dirname = os.path.basename(os.getcwd())
            print("[{}] ".format(dirname), end='\n')
            # print("OK")

    # Collect and return all the flags in flag_dict
    all_cxxflags = (" ".join(flag_dict.values()) + " " +
                    " ".join(global_flag_dict.values())).strip()

    if all_cxxflags:
        return split_cxxflags(all_cxxflags, win64)

    # CFLAGS, defines and libs not found
    return "", "", "", "", "", ""


def get_main_source_file(test_sources=None):
    """Get the main source file. It may be named main.cpp, main.cc, main.cxx, main.c,
    or be the only one, or the one containing 'main('. Return a blank string if none is found."""
    for ext in ["cpp", "cc", "cxx", "c"]:
        if os.path.exists("main." + ext):
            return "main." + ext
    # No main source file, see if there is only one non-test source file there
    if not test_sources:
        test_sources = get_test_sources()
    all_sources = [fname for fname in chain(
        iglob("*.cpp"), iglob("*.cc"), iglob("*.cxx"), iglob("*.c")) if fname not in test_sources]
    if len(all_sources) == 0:
        # No main source
        return ""
    if len(all_sources) == 1:
        # Look at the one source file that was found
        fname = all_sources[0]
        try:
            data = open(fname).read()
            if " main(" in data:
                return fname
            elif "\nmain(" in data:
                return fname
        except:
            print("Could not read " + fname)
            exit(1)
        # The one source file that was found did not contain " main("
        return ""
    # Multiple candidates for the main source file, use the one that contains " main("
    for fname in all_sources:
        try:
            if " main(" in open(fname).read():
                return fname
        except:
            print("Could not read " + fname)
            exit(1)
    # No source file contained "main(", there may not be a main source file here
    return ""


def get_test_sources():
    """Get all source files ending with _test.cpp, _test.cc, _test.cxx or named test.cpp, test.cc or test.cxx"""
    test_sources = list(chain(iglob("*_test.cpp"), iglob("*_test.cc"), iglob("*_test.cxx"), iglob("*_test.c")))
    for ext in "cpp", "cc", "cxx", "c":
        if os.path.exists("test." + ext):
            test_sources.append("test." + ext)
            break
    return test_sources


def get_dep_sources(main_source_file=None, test_sources=None):
    """Get all source files that the main executable, or test executables, may depend upon"""
    if not test_sources:
        test_sources = get_test_sources()
    if not main_source_file:
        main_source_file = get_main_source_file(test_sources)
    return [fname for fname in chain(iglob("*.cpp"), iglob("*.cc"), iglob("*.cxx"), iglob("*.c")) if (fname != main_source_file) and (fname not in test_sources)]


def strip_ext(filenames):
    """Remove filename extensions from the list of filenames"""
    return [os.path.splitext(fname)[0] for fname in filenames]


def add_flags(env, src_file, system_include_dirs, win64, compiler_includes):
    """Add build flags to the environment"""
    includes, defines, libs, libpaths, linkflags, other_cxxflags = get_buildflags(
        src_file, system_include_dirs, win64, compiler_includes, str(env["CXX"]))
    if includes:
        if "CPPPATH" in env:
            newincs = [inc for inc in includes.split(" ") if inc.lower() not in str(env["CPPPATH"]).lower()]
            if newincs:
                for newinc in newincs:
                    if newinc not in compiler_includes:
                        env.Append(CPPPATH=newinc)
        else:
            for include in includes.split(" "):
                env.Append(CPPPATH=include)
    if defines:
        if "CPPDEFINES" in env:
            newcppdefs = [cppdef for cppdef in defines.split(" ") if cppdef not in str(env["CPPDEFINES"])]
            if newcppdefs:
                for newdef in newcppdefs:
                    env.Append(CPPDEFINES=newdef)
        else:
            for define in defines.split(" "):
                env.Append(CPPDEFINES=define)
    if libs:
        if "LIBS" in env:
            newlibs = [lib for lib in libs.split(" ") if lib not in str(env["LIBS"])]
            if newlibs:
                env.Append(LIBS=newlibs)
        else:
            env.Append(LIBS=libs.split(" "))
    if libpaths and libpaths not in str(env["LINKFLAGS"]):
        env.Append(LINKFLAGS=" " + libpaths)
    if linkflags and linkflags not in str(env["LINKFLAGS"]):
        env.Append(LINKFLAGS=" " + linkflags)
    if other_cxxflags and other_cxxflags not in str(env["CXXFLAGS"]):
        env.Append(CXXFLAGS=" " + other_cxxflags)


def supported(cxx, std):
    """Check if the given compiler supports the given standard. Example: supported("g++", "c++2a")"""
    # Tested with clang++ and g++-7
    cmd = "echo asdf | " + cxx + " -std=" + std + " -x c++ -E - 2>&1 | grep -q -v \"" + std + "\" && echo YES || echo NO"
    try:
        return os.popen2(cmd)[1].read().strip() == "YES"
    except OSError:
        # Assume that this is an unknown compiler and that it does support the given standard.
        # This lets the compiler fail by itself a bit further in the process, instead of stopping a working compiler from being used.
        return True


def cxx_main():
    """The main function"""

    # Make sure to use the --compress or --tmpdir flag when using GNU parallel
    SConsignFile("/tmp/cxx")  # will be stored as /tmp/cxx.dblite

    # Include paths on the system, as reported by the compiler
    compiler_includes = []

    # Test ELF-files to be generated. Don't add "test" here since it may be passed back to this file as an argument!
    test_sources = get_test_sources()

    # Main ELF-file to be generated
    main_source_file = get_main_source_file(test_sources)

    # Prepare to check if we are compiling for 64-bit Windows or not
    win64 = bool(int(ARGUMENTS.get('win64', 0)))  # win64=1
    # Prepare to check if the main source file uses OpenMP
    openmp = False
    # Prepare to check if the main source file lets GLFW include Vulkan
    glfw_vulkan = False
    boost = False
    filesystem = False
    mathlib = False
    try:
        for line in open(main_source_file).read().split(os.linesep):
            # Check if "#include <windows.h>" exists in the main source file
            for win_include in ('#include <windows.h>', '#include "windows.h"', '#include<windows.h>'):
                if win_include in line:
                    win64 = True
                    break
            # Check if OpenMP is used in the main source file
            if "#pragma omp" in line:
                openmp = True
            # Check if GLFW_INCLUDE_VULKAN is defined in the main source file
            if "#define GLFW_INCLUDE_VULKAN" in line:
                glfw_vulkan = True
            # Check if boost is included
            if "#include <boost/" in line:
                boost = True
            # Check if filesystem is included
            if "#include <filesystem>" in line:
                filesystem = True
            # Check if cmath or math.h is included
            if line.strip() in ('#include <cmath>', '#include "math.h"'):
                mathlib = True
    except IOError:
        pass

    # Find all source files that are not the main source file and not test files
    dep_src = get_dep_sources(main_source_file, test_sources)

    # Test executables to be built
    test_elves = []
    if test_sources:
        test_elves = strip_ext(test_sources)

    # Main executable to be built
    main_executable = ""
    if main_source_file:
        current_directory_name = os.path.basename(os.path.normpath(os.getcwd()))
        if current_directory_name != "src":
            main_executable = current_directory_name
        else:
            main_executable = os.path.splitext(main_source_file)[0]
        # Add .exe extension for 64-bit Windows executables
        if win64:
            main_executable += ".exe"

    # Custom command line targets
    if 'clean' in COMMAND_LINE_TARGETS:  # Clean built executables and object files
        if (not test_elves) and (not main_executable):
            print("Nothing to clean")
            exit(0)
        # Also remove main.exe, if it's there, and win64=1
        if win64 and os.path.exists(main_executable + ".exe"):
            os.remove(main_executable + ".exe")
            print("Removed {}.exe".format(main_executable))
        # Remove all profiling files
        for fn in list(chain(iglob("*.profraw"), iglob("*.gcda"), iglob("*.gcno"))):
            os.remove(fn)
            print("Removed {}".format(fn))
        # Remove scons files
        for fn in list(iglob(".sconsign.dblite")):
            os.remove(fn)
            print("Removed {}".format(fn))
        # Remove all object files, not just the one from the build graph
        # for fn in list(iglob("*.o")):
        #    os.remove(fn)
        #    print("Removed {}".format(fn))
        # Replace the "clean" argument with "-c", and list all targets
        cmd = [x for x in argv if x != "clean"] + ["-c"] + [main_executable] + test_elves
        # Clean
        status, output = getstatusoutput(" ".join(cmd))
        output = output.strip()
        if output:
            print(output)
        exit(status)
    elif 'testbuild' in COMMAND_LINE_TARGETS:  # Build and run tests, this is the default
        # Remove the "test" argument, and list all test-executable targets
        cmd = ""
        if test_elves and main_executable:
            cmd = [x for x in argv if x != "testbuild"] + \
                [elf for elf in test_elves + [main_executable] if elf != "testbuild"]
        elif test_elves:
            cmd = [x for x in argv if x != "testbuild"] + \
                [elf for elf in test_elves if elf != "testbuild"]
        elif main_executable:
            cmd = [x for x in argv if x != "testbuild"] + \
                [elf for elf in [main_executable] if elf != "testbuild"]
        elif os.path.basename(os.path.abspath(os.curdir)) in ["common", "include"]:
            print("Nothing to test")
            exit(0)
        else:
            print("Nothing to build")
            exit(0)
        # Build the tests/executable
        status, output = getstatusoutput(" ".join(cmd))
        output = output.strip()
        if output:
            print(output)
        exit(status)
    elif 'test' in COMMAND_LINE_TARGETS and main_executable != "test":  # Build and run tests
        if not test_elves:
            print("Nothing to test")
            exit(0)
        # Remove the "test" argument, and list all test-executable targets
        cmd = [x for x in argv if x != "test"] + [elf for elf in test_elves if elf != "test"]
        # Build the tests
        try:
            output = check_output(cmd)
        except:
            #print("Could not run: " + " ".join(cmd))
            exit(1)
        output = os.linesep.join([line for line in output.split(
            os.linesep) if not "up to date" in line]).strip()
        if output:
            print(output)
        # Run the tests
        for test_elf in test_elves:
            status, output = getstatusoutput(os.path.join(".", test_elf))
            output = output.strip()
            if output:
                print(output)
            # Exit on error
            if status != 0:
                exit(status)
        exit(0)
    elif 'run' in COMMAND_LINE_TARGETS:  # Build and run main
        # TODO: if win64==True, build an .exe and run it with wine
        # Remove the "run" argument, and add "main"
        cmd = [x for x in argv if x != "run"] + [main_executable]
        # Check if any main source file exists
        if not main_source_file:
            print("Nothing to run (no main source file)")
            exit(0)
        # Build main
        try:
            output = check_output(cmd)
        except:
            #print("Could not run: " + " ".join(cmd))
            exit(1)
        output = os.linesep.join([line for line in output.split(
            os.linesep) if not "up to date" in line]).strip()
        if output:
            print(output)
            # Flush stdout
            stdout.flush()
        # Get arguments passed with args="..." (the arguments after -- on the cxx command line)
        given_args = []
        if 'args' in ARGUMENTS:
            given_args = ARGUMENTS['args']
        # Run the first main elf
        if win64:
            if len(given_args) > 1:
                print("wine " + main_executable + " " + " ".join(given_args.split()))
            os.execvp("wine", ["wine", main_executable] + given_args.split())
        else:
            executable = os.path.join(".", main_executable)
            if len(given_args) > 1:
                print(executable + " " + " ".join(given_args.split()))
            os.execvp(executable, [executable] + given_args.split())
        exit(0)

    # Set the number of jobs to the number of CPUs
    SetOption('num_jobs', cpu_count())

    # Random build-order, for the possibility of using the cache better
    SetOption('random', 1)

    # Create an environment
    env = Environment()

    # Faster checks of existing code
    env.Decider('MD5-timestamp')

    # Use the given CXX as the default value for the C++ compiler
    if 'CXX' in ARGUMENTS:
        env.Replace(CXX=ARGUMENTS['CXX'])

    # check if "clean" is being run
    cleaning = env.GetOption('clean') or ('clean' in COMMAND_LINE_TARGETS)

    # If "win64" is set, use the mingw32 g++ compiler
    if win64:
        # Check if looks like no Windows-related compiler is given, or not
        if env["CXX"] in ["g++", "c++"]:
            # Assume that a Windows-related compiler is not specified
            if which("x86_64-w64-mingw32-g++"):
                env.Replace(CXX="x86_64-w64-mingw32-g++")
            elif which("docker"):
                docker_image = "jhasse/mingw:latest"
                print("x86_64-w64-mingw32-g++ is missing from PATH, using this docker image instead: " + docker_image)
                # Older versions of docker needs trickery with "sh -c" instead of just setting the working directory with "-w"
                try:
                    docker_major_version = int(os.popen2("docker --version")[1].read().split(" ")[2].split(".")[0])
                except:
                    docker_major_version = 0
                if docker_major_version >= 18:
                    # For newer versions of docker
                    docker_cxx = "docker run -v \"" + \
                        os.path.abspath(os.path.curdir) + ":/home\" -w /home --rm " + \
                        docker_image + " x86_64-w64-mingw32-g++"
                else:
                    # For older versions of docker
                    docker_cxx = "docker run -v \"" + \
                        os.path.abspath(os.path.curdir) + ":/home\" --rm " + docker_image + \
                        ' sh -c "cd /home; /usr/bin/x86_64-w64-mingw32-g++ $_"'
                env.Replace(CXX=docker_cxx)
            else:
                print("error: Could not find a compiler for producing 64-bit Windows executables. Neither x86_64-w64-mingw32-g++ nor docker were found.")
                exit(1)
    elif int(ARGUMENTS.get('zap', 0)):
        # zapc++ looks for include files in the wrong place unless --gcc-toolchain=/usr is given
        env.Append(CXXFLAGS=' --gcc-toolchain=/usr -std=c++14')
    else:
        # Check if a particular C++ compiler is given, or not
        if str(env["CXX"]) == "c++" or (str(env["CXX"]) == "g++" and platform.system() == "NetBSD"):
            compiler_binaries = ["g++-9", "g++9", "g++-8", "g++8", "g++-7", "g++7", "g++-HEAD", "eg++", "g++"]
            if platform.system() == "Darwin":
                # if on macOS, try clang++ first
                compiler_binaries = ["clang++"] + compiler_binaries
            elif platform.system() == "NetBSD":
                if exe("/usr/pkg/gcc9/bin/g++"):
                    # if on NetBSD, try /usr/bin/pkg/gcc9 first
                    compiler_binaries = ["/usr/pkg/gcc9/bin/g++"] + compiler_binaries
                elif exe("/usr/pkg/gcc8/bin/g++"):
                    # if on NetBSD, try /usr/bin/pkg/gcc8 first
                    compiler_binaries = ["/usr/pkg/gcc8/bin/g++"] + compiler_binaries
                elif exe("/usr/pkg/gcc7/bin/g++"):
                    # if on NetBSD, try /usr/bin/pkg/gcc7 second
                    compiler_binaries = ["/usr/pkg/gcc7/bin/g++"] + compiler_binaries
            elif exe("/usr/bin/pacman"):
                # if on Arch Linux, try g++ first, since it's usually up to date
                compiler_binaries = ["g++"] + compiler_binaries

            found_compiler = ""
            found_cppstd = ""

            # Only check if the compiler supports the std if no "std=" is given
            for std in "c++2a", "c++17", "c++14", "c++11":
                for compiler in compiler_binaries:
                    if which(compiler) and supported(compiler, std):
                        found_compiler = compiler
                        found_cppstd = std
                        break
                else:
                    print("WARNING: No compiler with support for " + std + " was found")
                if found_compiler:
                    break
            else:
                print("WARNING: No compiler with support for C++17, C++14 or C++11 was found, tried these: " + str(compiler_binaries))
                exit(1)

            if found_compiler:
                # Use the compiler if it exists in path and supports the standard
                env.Replace(CXX=compiler)
            if found_cppstd and not ARGUMENTS.get('std', ''):
                if not main_source_file.endswith(".c") and ("-std=" not in str(env["CXXFLAGS"])):
                    env.Append(CXXFLAGS=' -std=' + found_cppstd)

            # clang is set?
            if int(ARGUMENTS.get('clang', 0)):
                env.Replace(CXX='clang++')
            elif int(ARGUMENTS.get('zap', 0)):
                env.Replace(CXX='zapcc++')

    if platform.system() == "OpenBSD" and str(env["CXX"]) == "g++":
        env.Replace(CXX="/usr/local/bin/eg++")

    if not cleaning:  # ) and (not main_source_file.endswith(".c")):
        if not bool(ARGUMENTS.get('std', '')):
            # std is not set, use the latest possible C++ standard flag
            if "-std=" not in str(env["CXXFLAGS"]):
                env.Append(CXXFLAGS=' -std=c++2a')
        elif not int(ARGUMENTS.get('zap', 0)):
            # if std is something else, use that
            args = []
            for key, value in ARGLIST:
                if key == 'std':
                    if supported(str(env["CXX"]), value):
                        if "-std=" + value not in str(env["CXXFLAGS"]):
                            env.Append(CXXFLAGS=' -std=' + value)
                    else:
                        try:
                            value_sub_3 = value[:-2] + str(int(value[-2:].replace('a', '0').replace('x', '0')) - 3)
                            print("WARNING: " + value + " is not supported by " +
                                  str(env["CXX"]) + ", using: " + value_sub_3)
                            if supported(str(env["CXX"]), value_sub_3):
                                if value in str(env["CXXFLAGS"]):
                                    new_cxxflags = " " + str(env["CXXFLAGS"]).replace(value, value_sub_3) + " "
                                    env.Replace(CXXFLAGS=new_cxxflags)
                                else:
                                    env.Append(CXXFLAGS=' -std=' + value_sub_3)
                            else:
                                print("WARNING:", value_sub_3, "is not supported by", str(env["CXX"]))
                        except ValueError:
                            print("WARNING: " + value + " is not supported by " + str(env["CXX"]))

        # Use the selected C++ compiler to report back all system include paths it will search automatically
        compiler_includes = []
        try:
            compiler_includes = [line.strip().split()[0] for line in os.popen2("echo | " + str(env["CXX"]) + " -E -Wp,-v - 2>&1")[
                1].read().split("\n") if line.strip().startswith("/") and os.path.exists(line.strip().split()[0])]
        except OSError:
            pass

        # imgdir/datadir/shaderdir/sharedir/resourcedir is set?
        for dirname in ["img", "data", "shader", "share", "resource"]:
            if ARGUMENTS.get(dirname + 'dir', ""):
                # only add system directories that have local equivalents (same or parent directory, singular or plural)
                if os.path.exists(dirname) or os.path.exists(os.path.join("..", dirname)) or os.path.exists(dirname + "s") or os.path.exists(os.path.join("..", dirname + "s")):
                    dir = os.path.normpath(ARGUMENTS[dirname + "dir"]) + os.path.sep
                    env.Append(CPPDEFINES=[dirname.upper() + "DIR='\"" + dir + "\"'"])
            else:
                # not specified on the commandline
                if os.path.exists(dirname):  # same directory
                    dir = os.path.normpath(dirname) + os.path.sep
                    env.Append(CPPDEFINES=[dirname.upper() + "DIR='\"" + dir + "\"'"])
                elif os.path.exists(os.path.join("..", dirname)):  # parent directory
                    dir = os.path.normpath(os.path.join("..", dirname)) + os.path.sep
                    env.Append(CPPDEFINES=[dirname.upper() + "DIR='\"" + dir + "\"'"])
                elif os.path.exists(dirname + "s"):  # same directory, plural
                    dir = os.path.normpath(dirname + "s") + os.path.sep
                    env.Append(CPPDEFINES=[dirname.upper() + "DIR='\"" + dir + "\"'"])
                elif os.path.exists(os.path.join("..", dirname + "s")):  # parent directory, plural
                    dir = os.path.normpath(os.path.join("..", dirname + "s")) + os.path.sep
                    env.Append(CPPDEFINES=[dirname.upper() + "DIR='\"" + dir + "\"'"])

        system_include_dirs = []
        if os.path.exists("/usr/include"):
            system_include_dirs.append("/usr/include")
        if which(str(env["CXX"])):
            machine_name = os.popen2(str(env["CXX"]) + " -dumpmachine")[1].read().strip()
            if os.path.exists("/usr/include/" + machine_name):
                system_include_dirs.append("/usr/include/" + machine_name)
        # Set system_include_dir[0] to the given value, or keep it as /usr/include
        if ARGUMENTS.get('system_include_dir', ''):
            system_include_dirs[0] = ARGUMENTS['system_include_dir']
        if platform.system() == "OpenBSD" and os.path.exists("/usr/local/include"):
            system_include_dirs.append("/usr/local/include")

        # print("SYSTEM_INCLUDE_DIRS", system_include_dirs)

        # debug is set?
        if int(ARGUMENTS.get('debug', 0)):
            env.Append(CXXFLAGS=' -Og -g -fno-omit-frame-pointer -fsanitize=address')
            if platform.system() != "Darwin":
                if env['CXX'] in ('clang++', 'zapcc++'):
                    # ie. Linux, clang, debug mode
                    env.Append(CXXFLAGS=' -static-libsan')
                else:
                    # ie. Linux, gcc, debug mode
                    env.Append(CXXFLAGS=' -static-libasan')
            env.Append(LINKFLAGS=' -fsanitize=address')
        # small is set?
        elif int(ARGUMENTS.get('small', 0)):
            env.Append(CXXFLAGS=' -Os -ffunction-sections -fdata-sections')
            env.Append(LINKFLAGS=' -ffunction-sections -fdata-sections -Wl,-s -Wl,-gc-sections')

        # opt is set?
        elif int(ARGUMENTS.get('opt', 0)):
            # Enable more optimization flags than O3 + link time optimization
            env.Append(CXXFLAGS=' -Ofast')
            # Use -flto for link-time optimization
            env.Append(CXXFLAGS=' -flto')
            env.Append(LINKFLAGS=' -Wl,-flto')
        elif openmp:
            # Use -O3 if OpenMP is in use
            env.Append(CXXFLAGS=' -O3')
        else:
            # Default optimization level
            env.Append(CXXFLAGS=' -O2')

        # Use -pipe for a possible speed increase when compiling
        env.Append(CXXFLAGS=' -pipe')

        # and -fPIC for position independent code. May increase the size of the executable.
        if not int(ARGUMENTS.get('small', 0)):
            env.Append(CXXFLAGS=' -fPIC')

        # if compiling for "tiny", don't use the standard library or exceptions
        if int(ARGUMENTS.get('tiny', 0)):
            env.Append(CXXFLAGS=' -s -nostdlib -fno-rtti -fno-ident -fomit-frame-pointer')
            env.Append(LINKFLAGS=' -Wl,-s -Wl,-z,norelro -Wl,--gc-sections')
            if main_source_file.endswith(".c"):
                if os.path.exists("/usr/bin/diet"):
                    env.Replace(CC='diet gcc')

        # Add two flags that are added by default if using qmake.
        # Don't use the flags if building for win64 with mingw.
        # Don't use the flags when in sloppy mode.
        # Don't use the flags when in small mode.
        if not win64 and (platform.system() == "Linux") and not int(ARGUMENTS.get('sloppy', 0)) and not int(ARGUMENTS.get('zap', 0)) and not int(ARGUMENTS.get('small', 0)):
            env.Append(CXXFLAGS=' -fno-plt -fstack-protector-strong')

        # There is only basic support for C
        if main_source_file.endswith(".c"):
            env.Append(LINKFLAGS=' -lm')
            cxxflags_to_cflags = str(env['CXXFLAGS']).replace('-std=c++2a', '-std=c11').replace('-fno-rtti', '')
            env.Append(CFLAGS=cxxflags_to_cflags)
            # Enable some macros
            if platform.system() == "Linux":
                #env.Append(CFLAGS=' -D_GNU_SOURCE')
                env.Append(CPPDEFINES=["_GNU_SOURCE"])
            elif 'bsd' in platform.system().lower():
                #env.Append(CFLAGS=' -D_BSD_SOURCE')
                env.Append(CPPDEFINES=["_BSD_SOURCE"])
            else:
                #env.Append(CFLAGS=' -D_XOPEN_SOURCE=700')
                env.Append(CPPDEFINES=["_XOPEN_SOURCE=700"])

        if os.path.exists("lib"):
            env.Append(LINKFLAGS=' -Llib -Wl,-rpath ./lib')
            for f in list(iglob("lib/*.so")):
                if f.startswith("lib/"):
                    f = f[4:]
                if f.startswith("lib"):
                    f = f[3:]
                if f.endswith(".so"):
                    f = f[:-3]
                env.Append(LINKFLAGS=' -l' + f)

        # Linux related build flags, for C (not C++)
        # if platform.system() == "Linux":
        #    #
        #    # Many options are available:
        #    #
        #    # _GNU_SOURCE
        #    # _XOPEN_SOURCE=700
        #    # _POSIX_C_SOURCE=200809L
        #    # _DEFAULT_SOURCE
        #    #
        #    # See:
        #    # https://stackoverflow.com/a/5583764/131264
        #    # https://stackoverflow.com/a/29201732/131264
        #    #
        #    env.Append(CPPDEFINES=["_GNU_SOURCE", "_BSD_SOURCE", "_DEFAULT_SOURCE"])

        # rec is set?
        if int(ARGUMENTS.get('rec', 0)):
            if env['CXX'] == 'g++':
                env.Append(CXXFLAGS=' -coverage -fprofile-generate -fprofile-correction')
                env.Append(LINKFLAGS=' -coverage -fprofile-generate -fprofile-correction')
            elif env['CXX'] in ('clang++', 'zapcc++'):
                env.Append(CXXFLAGS=' -fprofile-generate')
                env.Append(LINKFLAGS=' -fprofile-generate')
        else:
            if env['CXX'] == 'g++':
                if list(iglob("*.gcda")):
                    env.Append(CXXFLAGS=' -fprofile-use -fprofile-correction')
                    env.Append(LINKFLAGS=' -fprofile-use -fprofile-correction')
            elif env['CXX'] in ('clang++', 'zapcc++'):
                # if list(iglob("*.profraw")):
                    #cmd = "llvm-profdata merge -output=default.profdata default-*.profraw"
                    #output = os.popen2(cmd)[1].read().strip()
                    # print(output)
                if list(iglob("*.gcda")):
                    env.Append(CXXFLAGS=' -fprofile-use')
                    env.Append(LINKFLAGS=' -fprofile-use')

        # Windows related build flags
        if win64:
            env.Append(CXXFLAGS=' -Wno-unused-variable')
            if not main_source_file.endswith(".c"):
                env.Append(CPPFLAGS=' -mwindows')
                env.Append(LINKFLAGS=' -mwindows')
            env.Append(CPPFLAGS=' -lm')
            env.Append(LINKFLAGS=' -lm')
            # This could also work, for automatically adding ".exe":
            # env.Append(LINKFLAGS=' -Wl,--force-exe-suffix')

        # NetBSD related build flags
        if platform.system() == "NetBSD":
            env.Append(CPPFLAGS=' -L/usr/pkg/lib')
            env.Append(LINKFLAGS=' -L/usr/pkg/lib')

        # OpenBSD related build flags
        if platform.system() == "OpenBSD":
            env.Append(CPPFLAGS=' -L/usr/local/lib')
            env.Append(LINKFLAGS=' -L/usr/local/lib')

        # OpenMP related build flags
        if openmp:
            env.Append(CXXFLAGS=' -fopenmp')
            env.Append(LINKFLAGS=' -fopenmp -pthread -lpthread')

        # Boost thread related build flags
        if boost:
            env.Append(LINKFLAGS=' -pthread -lpthread')
            # Needed on NetBSD when using boost_thread
            env.Append(CXXFLAGS=' -Wno-unknown-pragmas')

        # GLFW + Vulkan related build flags
        if glfw_vulkan:
            env.Append(LINKFLAGS=' -lvulkan')

        # if sloppy is set, just try to build the damn thing
        if int(ARGUMENTS.get('sloppy', 0)):
            env.Append(CXXFLAGS=' -fpermissive -w')
            # Don't assume the compiler knows about any include directories
            compiler_includes = []
        else:
            # if sloppy is not set, add various warnings:

            # pretty strict + fail at first error
            env.Append(CXXFLAGS=' -Wall -Wshadow -Wpedantic -Wno-parentheses -Wfatal-errors -Wvla')

            # if strict is set, enable even more warnings
            if int(ARGUMENTS.get('strict', 0)):
                env.Append(CXXFLAGS=' -Wextra -Wconversion -Wparentheses -Weffc++')

        # Append any given CXXFLAGS after the other flags, to be able to override them
        if 'CXXFLAGS' in ARGUMENTS:
            env.Append(CXXFLAGS=ARGUMENTS['CXXFLAGS'])

    # add path to the include files
    env.Append(CPPPATH=LOCAL_INCLUDE_PATHS)

    # Find all included header files in ../include, then check if there are corresponding
    # sourcefiles in ../common and add them to dep_src, if there is a main source file
    if os.path.exists(main_source_file):
        includes = []
        has_new_include = True
        examined = []
        while has_new_include:
            has_new_include = False
            for INCLUDE_PATH in LOCAL_INCLUDE_PATHS:
                for filename in dep_src + [main_source_file] + [os.path.join(INCLUDE_PATH, x) for x in includes]:
                    if filename.lower() in examined:
                        continue
                    examined.append(filename.lower())
                    if os.path.exists(filename):
                        try:
                            new_includes = [line.split("\"")[1] for line in open(filename).read().split(
                                os.linesep)[:-1] if line.strip().startswith("#include \"")]
                        except IOError:
                            print("Can not read " + filename)
                            exit(1)
                    else:
                        continue
                    for new_include in [os.path.relpath(x) for x in new_includes]:
                        if new_include not in includes:
                            has_new_include = True
                            includes.append(new_include)
                for include in includes:
                    for COMMON_PATH in LOCAL_COMMON_PATHS:
                        for ext in [".cpp", ".cc", ".cxx", ".c"]:
                            source_filename = os.path.join(COMMON_PATH, include.rsplit(".", 1)[0] + ext)
                            if os.path.exists(source_filename):
                                if source_filename.lower() not in [x.lower() for x in dep_src]:
                                    dep_src.append(source_filename)

    # Find extra CFLAGS for the sources, if not cleaning
    if not env.GetOption('clean') and ('clean' not in COMMAND_LINE_TARGETS):
        for src_file in [main_source_file] + dep_src:
            add_flags(env, src_file, system_include_dirs, win64, compiler_includes)

    # If libraries are linked to, skip unused shared object dependencies.
    if "LIBS" in env and env["LIBS"]:
        # Neither --as-needed nor -zignore are supported when linking on macOS (Darwin)
        if platform.system() != "Darwin":
            env.Append(LINKFLAGS=' -Wl,--as-needed')
        elif platform.system() == "Solaris":
            env.Append(LINKFLAGS=' -Wl,-zignore')

        # Linking with boost_system must come last!
        for lib in env["LIBS"]:
            if lib.startswith("boost_") and "boost_system" not in env["LIBS"]:
                # check if boost_system is available from ldconfig before adding the lib
                if which('ldconfig'):
                    cmd = 'ldconfig -p | grep boost_system'
                    if "boost_system" in os.popen2(cmd)[1].read().strip():
                        env["LIBS"].append("boost_system")
                        break
                # if ldconfig is not available, check if it is in /usr/lib
                elif os.path.exists('/usr/lib/libboost_system.so'):
                    env["LIBS"].append("boost_system")
                    break

    # Link with '-lm', if needed
    if mathlib:
        if "LIBS" in env:
            env["LIBS"].append('m')
        else:
            env["LIBS"] = ['m']

    # Linking with libstdc++fs must come last!
    if filesystem:
        if "LIBS" in env:
            env["LIBS"].append('stdc++fs')
        else:
            env["LIBS"] = ['stdc++fs']

    # Build main executable
    if main_source_file:
        main = env.Program(main_executable, [main_source_file] + dep_src)

    # Find extra CFLAGS for the test sources, if not cleaning
    if not env.GetOption('clean') and ('clean' not in COMMAND_LINE_TARGETS):
        for src_file in test_sources:
            add_flags(env, src_file, system_include_dirs, win64, compiler_includes)

    # Remove non-existing includes
    includes = [include for include in env['CPPPATH'] if os.path.exists(include)]
    # Remove duplicate includes (in terms of pointing to the same directory)
    includemap = {}
    for include in includes:
        key = os.path.normpath(include).lower()
        if key in includemap:
            # use the shortest includepath, if several are specified for the same directory
            if len(include) < len(includemap[key]):
                if len(os.path.relpath(include)) < len(include):
                    includemap[key] = os.path.relpath(include)
                else:
                    includemap[key] = include
        else:
            if len(os.path.relpath(include)) < len(include):
                includemap[key] = os.path.relpath(include)
            else:
                includemap[key] = include
    new_includes = includemap.values()

    env.Append(CPPFLAGS=" " + " ".join(["-I" + x for x in new_includes if x != "." and x != ".."]))
    env.Replace(CPPPATH=[])
    # This also work for adding includes, but scons changes them to longer versions of the same path names
    # env.Replace(CPPPATH=new_includes)

    # Generate a QtCreator project file if "pro" is an argument
    if 'pro' in COMMAND_LINE_TARGETS:
        name = main_executable
        if name.endswith(".exe"):
            name = name[:-4]
        if os.path.exists(name + ".pro"):
            print("File already exists: " + name + ".pro")
            exit(1)
        project_file = open(name + ".pro", "w")
        project_file.write("TEMPLATE = app\n\n")
        project_file.write("CONFIG += c++2a\n")
        project_file.write("CONFIG -= console\n")
        project_file.write("CONFIG -= app_bundle\n")
        project_file.write("CONFIG -= qt\n\n")
        project_file.write("SOURCES += " + " \\\n           ".join([main_source_file] + sorted(dep_src)) + "\n\n")
        if 'LIBS' in env:
            project_file.write("LIBS += " + " \\\n        ".join(["-l" + x for x in env['LIBS']]) + "\n\n")
        project_file.write("INCLUDEPATH += " + " \\\n               ".join(sorted(new_includes)) + "\n\n")
        if 'CXX' in env:
            project_file.write("QMAKE_CXX = " + env['CXX'] + "\n")
        if 'CXXFLAGS' in env:
            # Don't treat warnings as errors when using QtCreator, since it's good at highlighting warnings by itself
            project_file.write("QMAKE_CXXFLAGS += " + " ".join(env['CXXFLAGS']).replace("-Wfatal-errors ", "") + "\n")
        if 'LINKFLAGS' in env:
            project_file.write("QMAKE_LFLAGS += " + " ".join(env['LINKFLAGS']) + "\n\n")
        if 'CPPDEFINES' in env:
            s = "DEFINES += "
            for define in env['CPPDEFINES']:
                if "=" in define:
                    name, value = define.split("=", 1)
                    s += name + '="' + value.replace(r'"', r'\"').replace("'\\\"", "'\\\"" + "$$_PRO_FILE_PWD_/") + '" '
                else:
                    s += define + ' '
            project_file.write(s.strip() + "\n")
        project_file.close()
        exit(0)

    # Set up non-default targets for all the test executables (based on *_test sources)
    for test_src in test_sources:
        test_elf = os.path.splitext(test_src)[0]
        env.Program(test_elf, [test_src] + dep_src)

    # Only main is the default target
    try:
        Default(main)
    except UnboundLocalError:
        try:
            if env.GetOption('test') or 'test' in COMMAND_LINE_TARGETS:
                print("Nothing to test")
                exit(0)
            else:
                print("Nothing to build")
        except AttributeError:
            pass


cxx_main()

# vim: ts=4 sw=4 et:
