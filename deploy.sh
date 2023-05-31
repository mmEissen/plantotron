#! /bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

git pull

poetry install --without=dev --sync

POETRY_PYTHON="$(poetry run which python)"

sudo "${POETRY_PYTHON}" -m plantotron install
