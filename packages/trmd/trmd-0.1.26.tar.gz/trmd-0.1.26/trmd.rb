class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/23/7d/8cbb199b99d328e5b914d5e69279b478013863bf8f1da33b03559fbf7535/trmd-0.1.25.tar.gz"
  sha256 "127c4d519bd83975e932e57c8ba19e8b525c8cb8835f74c20bdcb4b6643dfdee"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
