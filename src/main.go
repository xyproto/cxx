package main

import (
	"fmt"
)

type Env struct {
	CPPPATH    string
	CPPDEFINES string
	LIBS       string
	LINKFLAGS  string
	CXXFLAGS   string
	CXX        string
}

type BuildFlags struct {
	includes  []string
	defines   []string
	libs      []string
	libpaths  []string
	linkflags []string
	other     []string
}

// Create an Env from a BuildFlags struct
func (bf *BuildFlags) GetEnv() *Env {
	return &Env{}
}

func (f flag) startswith(prefix string) bool {
	return strings.HasPrefix(f, prefix)
}

func split_cxxflags(given_cxxflags string, win64 bool) *Env {
    /// Split a list of flags into includes (-I...), defines (-D...), libs (-l...), lib paths (-L...), linkflags (-Wl,) and other flags (-p, -F, -framework)
	includes := " "
	defines := " "
	libs := " "
	libpaths := " "
	linkflags := " "
	other := " "
	encountered_framework := false

    // Note that -Wl,-framework may appear in the given_cxxflags
	for flag := range [f.strip() for f in given_cxxflags.replace(" -framework ", " -framework" + SPECIAL_SYMBOLS).split(" ")]:
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
            if not win64 and " " + new_flag + " " not in linkflags:
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
            print("WARNING: Unsupported flag: " + flag)
            continue
    # Other CXXFLAGS can be returned as the final value here
    return includes.strip(), defines.strip(), libs.strip(), libpaths.strip(), linkflags.strip(), other.strip()




func main() {
	fmt.Println("hi")
}
