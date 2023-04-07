class CXX < Formula
  desc "Configuration-free build system for C++20 executables"
  homepage "https://github.com/xyproto/cxx"
  url "https://github.com/xyproto/cxx.git",
      :tag => "3.3.3",
      :revision => "asdf"
  sha256 "asdf"
  version_scheme 1
  head "https://github.com/xyproto/cxx.git"

  bottle do
    cellar :any_skip_relocation
    sha256 "asdf" => :high_sierra
    sha256 "asdf" => :sierra
    sha256 "asdf" => :el_capitan
  end

  depends_on "make" => :run
  depends_on "scons" => :run
  depends_on "pkg-config" => :run
  # gcc@9
  depends_on "gcc" => :recommended
  depends_on "clang-format" => :recommended
  depends_on "mingw-w64" => :recommended
  depends_on "wine" => :optional
  depends_on "valgrind" => :optional
  depends_on "gprof2dot" => :optional
  depends_on "graphviz" => :optional

  def install
    #rm "LICENSE"
    system "make", "PREFIX=#{prefix}", "install"
  end

  test do
    begin
      version = shell_output("#{bin}/cxx version")
      assert_match /CXX:/m, version
    end
  end
end
