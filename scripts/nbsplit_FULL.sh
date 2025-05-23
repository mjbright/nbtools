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

FULL_IPYNB=FULL_NOTEBOOK/FULL.multiline.ipynb
## FULL_MD_0=FULL_NOTEBOOK/OP_MODE_FULL.md
case $TOOL in
    tofu)      FULL_MD=FULL_NOTEBOOK/OP_OTF_OP_MODE_FULL.md;;
    terraform) FULL_MD=FULL_NOTEBOOK/OP_TF_OP_MODE_FULL.md;;
esac

## [ ! -f $FULL_MD_0 ] && die "No such output markdown file: $FULL_MD_0"
## cp $FULL_MD_0 $FULL_MD

[ ! -f $FULL_IPYNB ] && die "No such input notebook file: $FULL_IPYNB"
[ ! -f $FULL_MD ] && die "No such output markdown file: $FULL_MD"

NB_START=$(grep -c '#START:' $FULL_IPYNB)
NB_END=$(grep -c '#END:' $FULL_IPYNB)
MD_START=$(grep -c '#START:' $FULL_MD)
MD_END=$(grep -c '#END:' $FULL_MD)

STOP=0
echo "Notebook has $NB_START START blocks, markdown has $MD_START"
echo "Notebook has $NB_END END blocks, markdown has $MD_END"
[ "$NB_START" != "$MD_START" ] && { STOP=1; echo "Error: Notebook has $NB_START START blocks, markdown has only $MD_START"; }
[ "$NB_END"   != "$MD_END"   ] && { STOP=1; echo "Error: Notebook has $NB_END END blocks, markdown has only $MD_END"; }

ls -al $FULL_MD
[ $STOP -ne 0 ] && exit

set -x
~/scripts/nbsplit_full.py $FULL_MD
set +x

