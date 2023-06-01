#! /bin/bash

set -ex

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

git fetch
git checkout $GITHUB_SHA

/home/momo/.local/bin/poetry install -n --ansi --without=dev --sync

POETRY_PYTHON="$(/home/momo/.local/bin/poetry run -n --ansi which python)"
/usr/bin/sudo "${POETRY_PYTHON}" -m plantotron install
