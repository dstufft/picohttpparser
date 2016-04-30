#!/bin/bash

set -e
set -x

if [[ "${TOXENV}" == "pypy" ]]; then
    rm -rf ~/.pyenv
    git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    PYENV_ROOT="$HOME/.pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    pyenv install pypy-5.1
    pyenv global pypy-5.1
fi

pip install -U pip setuptools wheel
pip install -U tox codecov
