#!/bin/bash

IPYNB=$1; shift
OLD_NUM=$1; shift
NEW_NUM=$1; shift

SCRIPT=$( basename $0 )

die() { echo -e "$0: die - $*" >&2; exit 1; }

[ -z "${IPYNB}" ] && die "IPYNB parameter missing\n\n\tUsage: $SCRIPT <ipynb> <old_num> <new_num>"
[ ! -f ${IPYNB} ] && die "No such file '$IPYNB'"
jq '.' $IPYNB >/dev/null || die "Invalid json: Input file $IPYNB"
echo "Valid json: $IPYNB"
[ -z "$OLD_NUM" ] && die "OLD_NUM parameter missing\n\n\tUsage: $SCRIPT <ipynb> <old_num> <new_num>"
[ -z "$NEW_NUM" ] && die "NEW_NUM parameter missing\n\n\tUsage: $SCRIPT <ipynb> <old_num> <new_num>"


#sed -e '/^ *\"# '$OLD_NUM'/  \"# '$NEW_NUM'/' \
OPYNB=~/tmp/renumbered.ipynb
sed < $IPYNB > $OPYNB \
    -e "s/^ *\"# Lab*$OLD_NUM/    \"# Lab $NEW_NUM/" \
    -e "s/^ *\"# Lab*$OLD_NUM/    \"# Lab $NEW_NUM/" \
    -e "s/^ *\"# Lab *$OLD_NUM/    \"# Lab $NEW_NUM/" \
    -e "s/^ *\"\(##*\) $OLD_NUM/    \"\1 $NEW_NUM/" \
    -e "s/ lab$OLD_NUM/ lab$NEW_NUM/" \
    -e "s/\/lab$OLD_NUM/\/lab$NEW_NUM/" \

echo; echo "Effect of renumbering from $OLD_NUM to $NEW_NUM:"
read -p "Press <enter> to continue"

grep -v NB_DEBUG < $IPYNB > ~/tmp/original.nodebug.ipynb
grep -v NB_DEBUG < $OPYNB > ~/tmp/renumbered.nodebug.ipynb
#diff $IPYNB ~/tmp/renumbered.ipynb | grep -v NB_DEBUG | less
diff ~/tmp/original.nodebug.ipynb ~/tmp/renumbered.nodebug.ipynb | less
jq '.' $OPYNB >/dev/null || die "Invalid json: Output file $OPYNB"
echo "Valid json: $OPYNB"

CK1=$( cksum < $IPYNB )
CK2=$( cksum < $OPYNB )
if [ "$CK1" = "$CK2" ]; then
    echo "No differences"
    exit
fi

read -p "Overwrite $IPYNB (type 'yes') ..." YES
if [ "$YES" = "yes" ]; then
    set -x
        mkdir -p other/
        mv $IPYNB other/${IPYNB}.bak
        mv $OPYNB $IPYNB
    set +x
fi
exit

