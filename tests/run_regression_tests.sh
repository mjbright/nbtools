#!/usr/bin/env bash

cd $( dirname $0 )

export STUDENT=student

ALL=1
DIRS=""

## -- Func: --------------------------------------------

die() { echo "$0: die - $*" >&2; exit 1; }

TEST_DIR() {
    DIR=$1

    cd $DIR/

    . ./env.rc
    # NB_NAME="Lab1.InstallTerraform"
    # NB_MODE="Terraform"
    # NB_PRIO=10
    
    ipynb=${NB_NAME}.ipynb
    ipynb_fmt=${NB_NAME}.ipynb.fmt

    REFERENCE_ipynb=${NB_NAME}.ipynb.REFERENCE
    REFERENCE_ipynb_fmt=${NB_NAME}.ipynb.REFERENCE.fmt

    [ ! -f ${REFERENCE_ipynb}     ] && die "[$PWD] No reference file - expected ${REFERENCE_ipynb}"
    [ ! -f ${REFERENCE_ipynb_fmt} ] && jq .  < ${REFERENCE_ipynb} > ${REFERENCE_ipynb_fmt}

    read -p "[$PWD] About to initialize"
    . ~/scripts/nbtool.rc $NB_PRIO $NB_MODE "$NB_NAME"

    read -p "About to generalize new filtered notebook"
    NB_QUIET

    jq . <$ipynb >$ipynb_fmt
    wc -l $ipynb $ipynb_fmt

    CMD="diff $ipynb_fmt ${REFERENCE_ipynb_fmt}"
    echo "-- $CMD"
    read -p "About to compare generated ipynb against reference"
    $CMD

    cd -
}

## -- Args: --------------------------------------------

while [ ! -z "$1" ]; do
    case $1 in
        */) DIRS=$1;;
    esac
    shift
done

## -- Main: --------------------------------------------

[ -z "$DIRS" ] && DIRS=$( ls -1d */ )

echo "DIRS=$DIRS"

#. ../scripts/nbtool.rc

for DIR in $DIRS; do
    #echo "==== ./$DIR/test.sh"
    #./$DIR/test.sh
    TEST_DIR $DIR/
done

