class Sakemake < Formula
  desc "Configuration-free build system for C++17 executables"
  homepage "https://github.com/xyproto/sakemake"
  url "https://github.com/xyproto/sakemake.git",
      :tag => "1.45",
      :revision => "1050ddd2f60bcde4d8a1485fc66cfa14a91d275b"
  sha256 "f1627ed11e84890befbf244828aff7a56a17157f721b445804e18b5461e3b8f3"
  version_scheme 1
  head "https://github.com/xyproto/sakemake.git"

  bottle do
    cellar :any_skip_relocation
    sha256 "75251e63866d6e338b1a81ee6d5d007e9f4f6f80801cabe80a918be7cea976b7" => :high_sierra
    sha256 "1435aa8e578bc70ef7847ae191747e75140d04150b1cbf6d2f9f318f326e7453" => :sierra
    sha256 "b2a1778124b34030e3bf5aaf4f9356f8a07b4d0db9841a4cadd1b70e4e380fad" => :el_capitan
  end

  depends_on "make" => :run
  depends_on "scons" => :run
  depends_on "pkg-config" => :run
  depends_on "gcc@7" => :recommended
  depends_on "clang-format" => :recommended
  depends_on "mingw-w64" => :recommended
  depends_on "wine" => :optional
  depends_on "valgrind" => :optional
  depends_on "gprof2dot" => :optional
  depends_on "graphviz" => :optional
  depends_on "kcachegrind" => :optional

  def install
    system "make", "PREFIX=#{prefix}", "install"
  end

  test do
    begin
      version = shell_output("#{bin}/sakemake version")
      assert_match /Sakemake:/m, version
    end
  end
end
