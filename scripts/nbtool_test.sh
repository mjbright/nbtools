

IP_NB=~/src/mjbright.labs-terraform-private/tf-intro/10.Revision/IP_TF_Lab10.Revision.ipynb

#IP_NB=~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/IP_FULL.ipynb


#IP_NB=~/src/github.com/GIT_mjbright/labs-terraform-private/tf-intro/10.Revision/IP_TF_Lab10.Revision.ipynb
#src/github.com/GIT_mjbright/nbtools

## -- Func: ---------------------------------------------------------------------------

die() { echo "$0: die - $*">&2; exit 1; }

get_SRC_ROOT() {
    echo "-- get_SRC_ROOT $1"
    REF_DIR=$1; shift
    REF_DIR=$( echo $REF_DIR | sed 's?~?'$HOME'?' )

    #/Users/mjb/src/github.com/GIT_mjbright/nbtools

    #case $SRC_ROOT in
    case $REF_DIR in
        *src/github.com/GIT_mjbright*)
            SRC_ROOT=~/src/github.com/GIT_mjbright
            ABS_IP_NB=${SRC_ROOT}/${IP_NB}
            [ -z "$NBTOOL_DIR" ] && {
		NBTOOL_DIR=$SRC_ROOT/nbtools/scripts
	        [ $NBTOOL_VERSION -eq 2 ] && NBTOOL_DIR=$SRC_ROOT/nbtools/scripts/nbtools2
	    }
            ;;

        #*src/) IP_NB=~/src/mjbright.${IP_NB} ;;
	# .e.g. /home/student/src/mjbright.nbtools/scripts
	# .e.g. /home/student/src/mjbright.labs-terraform-private
        *src/mjbright.*)
            SRC_ROOT=~/src
            ABS_IP_NB=${SRC_ROOT}/mjbright.${IP_NB}
            [ -z "$NBTOOL_DIR" ] && {
		NBTOOL_DIR=$SRC_ROOT/mjbright.nbtools/scripts
	        [ $NBTOOL_VERSION -eq 2 ] && NBTOOL_DIR=$SRC_ROOT/mjbright.nbtools/scripts/nbtools2
	    }
            ;;

        *) die "[$REF_DIR] No matching src dir"
    esac
}

RUN_TEST() {
    if [ $ABS_PATH -eq 0 ]; then
        get_SRC_ROOT $PWD
    else
        get_SRC_ROOT ${IP_NB/%*}
    fi

    FILE=${IP_NB,,}
    FILE=${FILE##*/}
    case $FILE in
        ip_*lab[1-9]*)
	    #LAB_NUM=$( echo ${IP_NB} | sed -e 's/.*_lab//' -e 's/^\([^_]*)//' ) 
	    LAB_NUM=$( echo ${FILE} | sed -e 's/.*_lab//' -e 's/^\([^_,-,\.]*\)[_,-,\.].*/\1/' ) 
	    #LAB_NUM=$( echo ${FILE} | sed -e 's/.*_lab//' )
	    ;;

        ip_full*)
	    LAB_NUM="FULL";;

        *)  die "Failed to find lab number in $FILE";;
    esac

    case $LAB_NUM in
	[1-9])      ;;
	[1-9][0-9]) ;;

	FULL)       ;;

	*)          die "Failed to find numeric lab numberor 'FULL' in [$LAB_NUM] $IP_NB";;
    esac

    [ ${NBTOOL_VERSION} -eq 2 ] && {
	    echo "WAS: '$NBTOOL_DIR'"
	    NBTOOL_DIR=$NBTOOL_DIR/nbtools2
	    echo "WAS: '$NBTOOL_DIR'"
    }
    read -p "NBTOOL version $NBTOOL_VERSION"

    [ -z "$NBTOOL_RC"  ] && NBTOOL_RC=$NBTOOL_DIR/nbtool.rc
    [ -z "$NBTOOL_FN"  ] && NBTOOL_FN=$NBTOOL_DIR/nbtool.fn
    [ -z "$NBTOOL_PY"  ] && NBTOOL_PY=$NBTOOL_DIR/nbtool.py

    [ ! -d $NBTOOL_DIR ] && die "No such nbtool scripts dir '$NBTOOL_DIR'"
    [ ! -f $NBTOOL_RC  ] && die "No such nbtool.rc script as '$NBTOOL_RC'"
    [ ! -f $NBTOOL_FN  ] && die "No such nbtool.fn script as '$NBTOOL_FN'"
    [ ! -x $NBTOOL_PY  ] && die "No such nbtool.py script as '$NBTOOL_PY'"

    IP_DIR=${IP_NB%/*}
    [ ! -f $IP_NB ] && die "No such i/p notebook as $IP_NB"

    if [ "$LAB_NUM" = "FULL" ]; then
        OLD_OP_MD=$IP_DIR/OP_TF_OP_MODE_FULL.md
    else
        OLD_OP_MD=$IP_DIR/$( grep -m1 "/nbtool.rc .* OP_TF" $IP_NB | awk '{ print $5; }' | sed -e 's/" *$//' ).md
    fi
    [ ! -f $OLD_OP_MD ] && die "No such o/p markdown as $OLD_OP_MD"

    SUBDIR="unknown"
    case $IP_NB in
        */tf-intro/*) SUBDIR="tf-intro";;
        */tf-azure/*) SUBDIR="tf-azure";;
        */tf-adv-azure/*) SUBDIR="tf-adv-azure";;
	*) die "IP_NB Needs to be in recognized subdir - implemented in nbtool.rc"
    esac
    TMP=~/tmp/NBTOOLS/${SUBDIR}/${LAB_NUM}.test${NBTOOL_VERSION}
    mkdir -p ${TMP}
    echo ${TMP} | tee ${TMP}/.dir

    cp -a $IP_NB ${TMP}/

    IP_NB=${TMP}/${ABS_IP_NB##*/}
    [ ! -f $IP_NB ] && die "[tmp copy] No such i/p notebook as $IP_NB"

    ls -al $IP_NB
    sed -i.bak -e '/nbtool.rc / s/ OP_TF/ OP_TF_TEST/' $IP_NB
    #${TMP}/IP_TF_Lab10.Revision.ipynb
    ls -al $IP_NB

    diff $IP_NB{,.bak}

    cd ${TMP}/
    echo "-- [$PWD] -- [Lab $LAB_NUM] Processing notebook: -------------------------"
    read -p "RUN_TEST: About to process ... "
    
    NBTOOL_RC_args=$( grep -m1 "/nbtool.rc " $IP_NB | sed -e 's/"$//' -e 's/.*nbtool.rc //')
    
    [ -z "$NBTOOL_RC_args" ] && die "Failed to determine nbtool.rc arguments from notebook"
    #die "NBTOOL_RC_args='$NBTOOL_RC_args'"
    
    export JPY_SESSION_NAME=$IP_NB
    
    read -p "RUN_TEST: About to source $NBTOOL_RC ... "
    CMD="source $NBTOOL_RC $NBTOOL_RC_args"
    echo "-- $CMD"
    $CMD
    
    read -p "RUN_TEST: About to source $NBTOOL_FN ... "
    CMD="source $NBTOOL_FN"
    echo "-- $CMD"
    $CMD
    #exit
    
    #set -x
    read -p "RUN_TEST: About to call NB_QUIET ... "
    NB_QUIET
    
    echo; echo "-- Checking for die/occur in ~/tmp/quiet.filter.notebook.op"
    grep -iE "die|occur" ~/tmp/quiet.filter.notebook.op
    cp ~/tmp/quiet.filter.notebook.op $TMP/

    read -p "RUN_TEST: Checking for OP_*.md"
    NEW_OP_MD=$( ls -1tr ${TMP}/OP_*.md | tail -1 )
    read -p "RUN_TEST: DONE RUN_TEST"
}

## -- Args: ---------------------------------------------------------------------------

ABS_PATH=0
NBTOOL_VERSION=1

set -- -diff12

while [ ! -z "$1" ]; do
    case $1 in
        -2) NBTOOL_VERSION=2;;

	-diff12)
            SAVE_PWD=$PWD
	    read -p "1: About to run RUN_TEST "
            RUN_TEST
	    TMP1=$TMP
	    [ -z "$NEW_OP_MD" ] && die "1: NEW_OP_MD is unset"
            grep -v "Code-Cell" $NEW_OP_MD > $TMP1/new.md

            cd $SAVE_PWD
            NBTOOL_VERSION=2
	    read -p "2: About to run RUN_TEST "
            RUN_TEST
	    TMP2=$TMP
	    [ -z "$NEW_OP_MD" ] && die "2: NEW_OP_MD is unset"

	    set -x
	    ls -al $TMP1/
	    ls -al $TMP2/
	    set +x
	    read -p "Press ctrl-C"
	    #return
	    #exit
	    #XXX
            grep -v "Code-Cell" $NEW_OP_MD > $TMP2/new.md

	    ls -altr $TMP1/new.md $TMP2/new.md
	    wc   -l  $TMP1/new.md $TMP2/new.md
	    diff -w  $TMP1/new.md $TMP2/new.md

	    exit 0
	    ;;

        *.ipynb) IP_NB=$*; ABS_PATH=1;;

	*) die "Unknown arg '$1'";;
    esac
    shift
done

## -- Main: ---------------------------------------------------------------------------

RUN_TEST

ls -altr $OLD_OP_MD $NEW_OP_MD
grep -v "Code-Cell" $OLD_OP_MD > $TMP/old.md
grep -v "Code-Cell" $NEW_OP_MD > $TMP/new.md

ls -altr $TMP/old.md $TMP/new.md
diff  -w $TMP/old.md $TMP/new.md

wc -l    $TMP/old.md $TMP/new.md
ls -altr $TMP/old.md $TMP/new.md
echo; echo "-- About to show diffs"

read -p "Press <enter>"
#diff -w $OLD_OP_MD $NEW_OP_MD
diff -w $TMP/old.md $TMP/new.md | less -R
exit

