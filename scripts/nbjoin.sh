#!/usr/bin/env bash
#

REPO_DIR=~/src/mjbright.labs-terraform-private

TOFU=0
. ~/.tool
[ $OPENTOFU -ne 0 ] && TOFU=1

die() {
    echo >&2
    echo "PWD=$PWD" >&2
    echo -e "$0: die - $*" >&2; exit 1
}

[ "$1" = "-otf" ] && { OPENTOFU=1; TOFU=1; }
[ "$1" = "-tf"  ] && { OPENTOFU=0; TOFU=0; }
echo "TOFU=$TOFU OPENTOFU=$OPENTOFU TOOL_VERSION=$TOOL_VERSION TOOL=$TOOL"

SRC_DIR=tf-intro
case $PWD in
    */tf-intro*) SRC_DIR=tf-intro; FLAVOUR=intro;;
    */tf-azure*) SRC_DIR=tf-azure; FLAVOUR=azure;;
    */tf-adv-azure*) SRC_DIR=tf-adv-azure; FLAVOUR=adv-azure;;
    *) die "Move to tf-* directory\n\tunder $REPO_DIR";;
esac

#die "XX"

#exit
#
#cd $( dirname $0 )

# OP=~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL.ipynb
FULL_NB=FULL_NOTEBOOK/FULL.ipynb
FULL_NB_ML=${FULL_NB%.ipynb}.multiline.ipynb

IP_FILES=""
[ ! -f FULL_NOTEBOOK/IPFILES.rc ] && die "Missing file - FULL_NOTEBOOK/IPFILES.rc"
. FULL_NOTEBOOK/IPFILES.rc
[ -z "$IP_FILES" ] && die "IP_FILES not defined in FULL_NOTEBOOK/IPFILES.rc"

# How to order correctly?
#IP_FILES=$( ls -1 ~/src/mjbright.labs-terraform-private/tf-intro/[0-9]*.*/IP_TF_*.ipynb | grep -v STRETCH )

IP_FILES=$( echo $IP_FILES | sed 's?~?/home/student?g' )

python3 -m py_compile   ~/scripts/nbjoin.py || die "Syntax error"

set -x
~/scripts/nbjoin.py -nbtool -oN -op $FULL_NB \
    -oh FULL_NOTEBOOK/FULL_HEADER.ipynb \
    -od FULL_NOTEBOOK/FULL_BETWEEN.ipynb \
    -of FULL_NOTEBOOK/FULL_FOOTER.ipynb \
    \
    $IP_FILES || die "nbjoin.py failed"

set +x

#echo
#~/.venv/nbtoolbelt/bin/nbtb validate $FULL_NB -v

echo
~/scripts/nbcheck.py $FULL_NB || die "nbcheck.py failed - on $FULL_NB"
echo
~/scripts/nbcheck.py $FULL_NB_ML || die "nbcheck.py failed - on $FULL_NB_ML"

mv $FULL_NB_ML $FULL_NB
ls -al $FULL_NB
wc -cl $FULL_NB

