# LIC

<p align="center">
  <img src="https://github.com/kushvinth/lic/blob/main/assets/demo.gif?raw=true" alt="lic demo" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/kushvinth/lic" />
  <img src="https://img.shields.io/pypi/v/lic-cli" />
</p>

## Overview

A minimal, interactive license generator that fetches licenses from GitHub's official API.

No more going to GitHub, creating a file, typing 'LICENSE', picking a license, pushing and pulling. Just run `lic` and generate your license locally.

Works on **macOS, Linux, and Windows**.

## Installation

### Homebrew (macOS/Linux)

```bash
brew tap kushvinth/tap
brew install lic
```

### PyPI (recommended - cross-platform)

```bash
# Using uvx (recommended)
uvx lic-cli

# Or install globally with pipx
pipx install lic-cli

# Or with uv
uv tool install lic-cli
```

### From source

```bash
git clone https://github.com/kushvinth/lic.git
cd lic
uv venv
uv pip install -e .
```

## Usage

```bash
lic
```

## Contributing
- Fork the repository
- Create a branch
  ```bash
  git checkout -b contribution/blah-blah-blah
  ```
- Commit your changes and push to your branch
  ```bash
  git commit -m "made an blah-blah-blah"
  git push origin contribution/blah-blah-blah
  ```
- Open a pull request

---

<div align="center">
  Made by <a href="https://github.com/kushvinth">Kushvinth</a>
</div>
