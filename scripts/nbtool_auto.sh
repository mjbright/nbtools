#!/bin/bash

mkdir -p ~/tmp

die() { echo "$0: die - $*" >&2; exit 1; }

echo "---- Sourcing ~/scripts/nbtool.rc:"
source ~/scripts/nbtool.rc
touch ~/tmp/.nbtool.rc.read

# Variables already saved from notebook:
ls -al ~/tmp/LAB_vars.env
source ~/tmp/LAB_vars.env
set | grep ^LAB_.*=

[ ! -f README.ipynb ] && DIE "[$PWD] No such file as README.ipynb"
[ ! -f .converting  ] && touch .converting

echo
echo "---- Waiting for README.ipynb updates:"
while true; do
    python -m py_compile ~/scripts/nbtool.py || {
        die "ERROR: ~/scripts/nbtool.py"
    }

    [ ~/scripts/nbtool.rc -nt ~/tmp/.nbtool.rc.read ] &&
        source ~/scripts/nbtool.rc

    #[ $( find README.ipynb -newer .converting | wc -l ) != 0 ] && {
    [ README.ipynb -nt .converting ] && {
        echo; echo "---- EXCL_FN_LAB_ENV [$PWD]:"
        touch .converting
        EXCL_FN_LAB_ENV
        ls -altr
    }

    sleep 1
done

