class Lic < Formula
  desc "Minimal interactive license generator"
  version "0.1.2"
  homepage "https://github.com/kushvinth/lic"
  url "https://api.github.com/repos/SigireddyBalasai/lic/tarball/v0.1.2"
  sha256 "76de7967649a0cce61cf15a590db0cb823bd9eeab269fb1e7ed259f991b8e697"
  license "MIT"

  depends_on "python@3.12"
  depends_on "uv"

  def install
    python = Formula["python@3.12"].opt_bin/"python3.12"

    # Create venv WITHOUT pip (Homebrew style)
    system python, "-m", "venv", libexec

    # Install project using uv
    system Formula["uv"].opt_bin/"uv", "pip", "install",
           "--python", libexec/"bin/python",
           "--no-cache",
           buildpath

    # Expose CLI
    bin.install_symlink libexec/"bin/lic"
  end

  test do
    system bin/"lic", "--help"
  end
end