#!/bin/bash

mkdir -p ~/tmp

IPYNB=README.ipynb

DIR=$( basename $PWD )

ROOT=/home/student/src/mjbright.tf-scenarios-private/ServeUpLabs/content
LABS=azure

die() { echo "$0: die - $*" >&2; exit 1; }

CHECK_FILE_SIZE() {
    local FILE=$1; shift;
    local MIN_BYTES=$1; shift;

    #SIZE=$( stat -c %s $FILE )
    SIZE=$( wc -c < $FILE )
    [[ $SIZE -lt $MIN_BYTES ]] && {
        echo "File looks suspiciously small"
        ls -al $FILE
        return 1
    }
    return 0
}

SOURCE_NBTOOL_RC() {
    echo "----[$DIR] Sourcing ~/scripts/nbtool.rc:"
    source ~/scripts/nbtool.rc $*
    touch ~/tmp/.nbtool.rc.read ~/tmp/.nbtool.py.read
}

SOURCE_VARIABLES() {
    echo "----[$DIR] Sourcing ~/scripts/nbtool.rc:"
    source ~/scripts/nbtool.rc
    touch ~/tmp/.nbtool.rc.read ~/tmp/.nbtool.py.read

    # Variables already saved from notebook:
    ls -al ~/tmp/LAB_vars.env
    source ~/tmp/LAB_vars.env

    echo "==========================="
    set | grep -E "^(LAB_|NB_DIR)"
    echo "==========================="

    [ -z "$LAB_NUM" ] && {
        LAB_NUM=${LAB_NAME%%.*}
        LAB_NUM=${LAB_NUM#Lab}
    }

    DIR_NUM=${DIR%.*}
    if [ "$DIR_NUM" != "$LAB_NUM" ]; then
        echo "DIR_NUM:'$DIR_NUM' != LAB_NUM:'$LAB_NUM'"
        echo "Is this the correct directory       ?? [${PWD##*/}]"
        echo "Do the above variables look correct ??"
        echo -n "Enter y/n> "
        read DUMMY
        [ "$DUMMY" != "y" ] && exit
    fi

    [ ! -f $IPYNB ] && DIE "[$DIR] No such file as $IPYNB"

    LANG=$( jq -r '.metadata.kernelspec.language' $IPYNB )
    case $LANG in
        bash)
            [ ! -f $IPYNB_SH ] && { echo "Setting up pairing to bash";
                echo "Configuring $IPYNB for pairing:"
                CMD="jupytext --set-formats ipynb,sh:percent $IPYNB"
                echo "-- $CMD"; $CMD
            } ;;
    esac
}

CONVERT_1() {
    LAB_DIR=$1; shift

    NB="$LAB_DIR/$IPYNB"

    [ ! -d "$LAB_DIR" ] && die "No such directory as '$LAB_DIR'"
    [ ! -f "$NB"      ] && die "No such notebook '$NB'"
    cd $LAB_DIR
        ARGS=$( grep nbtool.rc $IPYNB | grep "Got args" | sed -e "s/.*Got args '//" -e "s/'.*//" )
        SOURCE_NBTOOL_RC $ARGS
        #SOURCE_VARIABLES
        #NB_INIT_NOTEBOOK
    cd -
}

CONVERT_ALL() {
    NBS=$( ls -1 $LABS_ROOT/$IPYNB )

    for NB in $NBS; do
        LAB_DIR=$( dirname $NB )
        CONVERT_1 $LAB_DIR
    done
}

while [ ! -z "$1" ]; do
    case $1 in
        *.ipynb) 
            IPYNB=$1
            IPYNB_SH=${IPYNB%.ipynb}.sh
            CONVERT_1 $IPYNB
            exit
            ;;
        -A) DO ALL sub-dirs
            LABS_ROOT=$ROOT/$LABS
            CONVERT_ALL $LABS_ROOT
            exit
            ;;
         #*) CONVERT_1 $1
            #exit
            #;;
    esac
done

IPYNB_SH=${IPYNB%.ipynb}.sh
SOURCE_NBTOOL_RC
SOURCE_VARIABLES

echo
echo "---- Waiting for $IPYNB updates:"
FIRST_LOOP=1
echo "Forcing conversion on first loop"
[ ! -f .converting  ] && touch .converting

while true; do
    python -m py_compile ~/scripts/nbtool.py || {
        die "ERROR: ~/scripts/nbtool.py"
    }

    [ ~/scripts/nbtool.py -nt ~/tmp/.nbtool.py.read ] && {
        echo "[$DIR] nbtool.py updated - NOT touching $IPYNB - but please save notebook"
    }

    [ ~/scripts/nbtool.rc -nt ~/tmp/.nbtool.rc.read ] && {
        source ~/scripts/nbtool.rc
        echo "[$DIR] nbtool.rc updated - NOT touching $IPYNB - but please save notebook"
    }

    #[ $( find $IPYNB -newer .converting | wc -l ) != 0 ] && {
    CONVERT=0
    [ $FIRST_LOOP  -eq 1           ] && { CONVERT=1; FIRST_LOOP=0; }
    [ $IPYNB -nt .converting ] && { CONVERT=1; }

    [ $CONVERT -eq 1 ] && {
        echo; echo "---- [$DIR] NB_LAB_ENV:"
        touch .converting
        #NB_LAB_ENV; #NB_FILTER_NOTEBOOK $IPYNB
        NB_INIT_NOTEBOOK
        ls -altr
        echo "-- <$DIR_NUM/$LAB_NUM> [$DIR]"
        touch ~/tmp/.nbtool.rc.read ~/tmp/.nbtool.py.read
    }

    CHECK_FILE_SIZE ${IPYNB%.ipynb}.md 1000 || {
        echo "Resourcing variables ..."
        SOURCE_VARIABLES
    }

    sleep 1
done

