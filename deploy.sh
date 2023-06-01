#! /bin/bash

set -ex

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

date
git fetch
date
git checkout $GITHUB_SHA
date
/home/momo/.local/bin/poetry install -n --ansi --without=dev --sync
date
POETRY_PYTHON="$(/home/momo/.local/bin/poetry run -n --ansi which python)"
date
/usr/bin/sudo "${POETRY_PYTHON}" -m plantotron install
date

