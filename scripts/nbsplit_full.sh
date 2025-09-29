#!/usr/bin/env bash

# cd $( dirname $0 )

REPO_DIR=~/src/mjbright.labs-terraform-private

die() {
    echo >&2
    echo "PWD=$PWD" >&2
    echo -e "$0: die - $*" >&2; exit 1
}

[ ! -f ~/.tool ] && die "No such file: ~/.tool"
. ~/.tool

[ "$1" = "-otf" ] && { OPENTOFU=1; TOFU=1; TOOL="tofu";      }
[ "$1" = "-tf"  ] && { OPENTOFU=0; TOFU=0; TOOL="terraform"; }

SRC_DIR=tf-intro
case $PWD in
    */tf-intro*) SRC_DIR=tf-intro; FLAVOUR=intro;;
    */tf-azure*) SRC_DIR=tf-azure; FLAVOUR=azure;;
    */tf-adv-azure*) SRC_DIR=tf-adv-azure; FLAVOUR=adv-azure;;
    *) die "Move to tf-* directory\n\tunder $REPO_DIR";;
esac

FULL_IPYNB=FULL_NOTEBOOK/IP_FULL.ipynb
FULL_ML_IPYNB=FULL_NOTEBOOK/IP_FULL.multiline.ipynb
## FULL_MD_0=FULL_NOTEBOOK/OP_MODE_FULL.md
[ ! -f $FULL_IPYNB ] && die "No such file as '$FULL_IPYNB'"

case $TOOL in
    tofu)      FULL_MD=FULL_NOTEBOOK/OP_OTF_OP_MODE_FULL.md;;
    terraform)
	    FULL_MD=FULL_NOTEBOOK/OP_TF_OP_MODE_FULL.md
	    # HACK:
	    cp FULL_NOTEBOOK/OP_MODE_FULL.md $FULL_MD
	    ;;
esac

## [ ! -f $FULL_MD_0 ] && die "No such output markdown file: $FULL_MD_0"
## cp $FULL_MD_0 $FULL_MD

jq . $FULL_IPYNB > $FULL_ML_IPYNB
[ ! -f $FULL_ML_IPYNB ] && die "No such input notebook file: $FULL_ML_IPYNB"
[ ! -f $FULL_MD       ] && die "No such output markdown file: $FULL_MD"

NB_START=$(grep -c '#START:' $FULL_ML_IPYNB)
NB_END=$(grep -c '#END:' $FULL_ML_IPYNB)
MD_START=$(grep -c '#START:' $FULL_MD)
MD_END=$(grep -c '#END:' $FULL_MD)

STOP=0
echo "Notebook is $FULL_IPYNB"
echo "ML Notebook is $FULL_ML_IPYNB"
echo "ML Notebook has $NB_START START blocks, markdown has $MD_START"
echo "ML Notebook has $NB_END END blocks, markdown has $MD_END"
[ "$NB_START" != "$MD_START" ] && { STOP=1; echo "Error: Notebook has $NB_START START blocks, markdown has only $MD_START"; }
[ "$NB_END"   != "$MD_END"   ] && { STOP=1; echo "Error: Notebook has $NB_END END blocks, markdown has only $MD_END"; }

ls -al $FULL_MD
[ $STOP -ne 0 ] && exit

set -x
~/scripts/nbsplit_full.py $FULL_MD
set +x

jq .  $FULL_IPYNB | grep -iq took && {
    TIMING=FULL_NOTEBOOK/took.${TOOL}_${TOOL_VERSION}.txt
    jq .  $FULL_IPYNB | grep -i took > $TIMING
    ls -al $TIMING
}

OP_FULL_MD=$( ls -1 -tr FULL_NOTEBOOK/OP_* | tail -1 )

echo; echo "Checking for Functions/Variables remaining in OP markdown [$OP_FULL_MD]"

echo "Checking for variables:"
read -p "Press <enter>"
grep '$__' $OP_FULL_MD

echo "Checking for TF functions:"
read -p "Press <enter>"
grep 'TF_' $OP_FULL_MD | grep -v TF_Intro | grep -v TF_VAR_ | grep -v TF_PLUGIN_CACHE_DIR |
    grep -v /OP_TF_Lab | grep -v /IP_TF_Lab | \
    grep -v /OP_OTF_Lab | grep -v /IP_OTF_Lab

echo "Checking for NB functions:"
read -p "Press <enter>"
grep 'NB_' $OP_FULL_MD | grep -v 'NB_SAVE -->'

