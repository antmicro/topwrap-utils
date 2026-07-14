# UV install path
export PATH := x"$PATH:$HOME/.local/bin"

default:
	@just --list

[arg("docs",long,value="1")]
install-debian-deps docs="0":
    #!/usr/bin/env bash
    apt-get update -qq
    apt-get install -y --no-install-recommends \
        curl \
        git \
        python3-dev \
        python3-pip \
        python3-venv \
        make

    if [[ {{docs}} == "1" ]];then apt-get install -y texlive-full imagemagick make chromium; fi

    curl -LsSf https://astral.sh/uv/install.sh | sh

# Run all configured linting checks.
test-lint:
	#!/usr/bin/env bash
	uv sync --extra lint
	# uv run pre-commit run check-yaml-extension --all-files
	uv run ruff format --check
	uv run ruff check
	uv run codespell

examples:
    #!/usr/bin/env bash
    uv sync
    uv pip install .
    uv run make -C examples -B

docs:
  #!/usr/bin/env bash
  cd docs/
  python3 -m venv .venv/
  source .venv/bin/activate
  python3 -m ensurepip
  pip3 install -r requirements.txt
  make html latexpdf
  cp build/latex/*.pdf build/html/

