

IP_NB=~/src/mjbright.labs-terraform-private/tf-intro/10.Revision/IP_TF_Lab10.Revision.ipynb


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

        *) die "Failed to find lab number in $FILE";;
    esac

    case $LAB_NUM in
	[1-9]) ;;
	[1-9][0-9]) ;;
	*) die "Failed to find numeric lab number in [$LAB_NUM] $IP_NB";;
    esac

    [ -z "$NBTOOL_RC"  ] && NBTOOL_RC=$NBTOOL_DIR/nbtool.rc
    [ -z "$NBTOOL_FN"  ] && NBTOOL_FN=$NBTOOL_DIR/nbtool.fn
    [ -z "$NBTOOL_PY"  ] && NBTOOL_PY=$NBTOOL_DIR/nbtool.py

    [ ! -d $NBTOOL_DIR ] && die "No such nbtool scripts dir '$NBTOOL_DIR'"
    [ ! -f $NBTOOL_RC  ] && die "No such nbtool.rc script as '$NBTOOL_RC'"
    [ ! -f $NBTOOL_FN  ] && die "No such nbtool.fn script as '$NBTOOL_FN'"
    [ ! -x $NBTOOL_PY  ] && die "No such nbtool.py script as '$NBTOOL_PY'"

    IP_DIR=${IP_NB%/*}
    [ ! -f $IP_NB ] && die "No such i/p notebook as $IP_NB"
    OLD_OP_MD=$IP_DIR/$( grep -m1 "/nbtool.rc .* OP_TF" $IP_NB | awk '{ print $5; }' | sed -e 's/" *$//' ).md
    [ ! -f $OLD_OP_MD ] && die "No such o/p markdown as $OLD_OP_MD"

    TMP=~/tmp/NBTOOLS/${LAB_NUM}.test${NBTOOL_VERSION}
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
    
    NBTOOL_RC_args=$( grep -m1 "/nbtool.rc " $IP_NB | sed -e 's/"$//' -e 's/.*nbtool.rc //')
    
    [ -z "$NBTOOL_RC_args" ] && die "Failed to determine nbtool.rc arguments from notebook"
    #die "NBTOOL_RC_args='$NBTOOL_RC_args'"
    
    export JPY_SESSION_NAME=$IP_NB
    
    CMD="source $NBTOOL_RC $NBTOOL_RC_args"
    echo "-- $CMD"
    $CMD
    
    CMD="source $NBTOOL_FN"
    echo "-- $CMD"
    $CMD
    #exit
    
    #set -x
    NB_QUIET
    
    echo; echo "-- Checking for die/occur in ~/tmp/quiet.filter.notebook.op"
    grep -iE "die|occur" ~/tmp/quiet.filter.notebook.op
    cp ~/tmp/quiet.filter.notebook.op $TMP/

    NEW_OP_MD=$( ls -1tr ${TMP}/OP_*.md | tail -1 )
}

## -- Args: ---------------------------------------------------------------------------

ABS_PATH=0
NBTOOL_VERSION=1

while [ ! -z "$1" ]; do
    case $1 in
        -2) NBTOOL_VERSION=2;;

	-diff12)
            SAVE_PWD=$PWD
            RUN_TEST
	    TMP1=$TMP
	    [ -z "$NEW_OP_MD" ] && die "1: NEW_OP_MD is unset"
            grep -v "Code-Cell" $NEW_OP_MD > $TMP1/new.md

            cd $SAVE_PWD
            NBTOOL_VERSION=2
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

