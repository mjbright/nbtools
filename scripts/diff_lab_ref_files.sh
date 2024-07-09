#!/bin/bash

REF="$HOME/src/mjbright.tf-scenarios/Solutions/tf-gen/2024-jun"
NEW="$HOME/labs/tf-gen.2024-jun"

REF=${REF%%/}
NEW=${NEW%%/}

if [ "$1" = "-allq" ]; then
    CMD="diff -rq $NEW/ $REF/"
    echo "-- $CMD"; $CMD
    exit
fi

if [ "$1" = "-all" ]; then
    CMD="diff -r $NEW/ $REF/"
    echo "-- $CMD"; $CMD
    exit
fi

#if [ "$1" = "-q" ]; then
    #CMD="diff -rq $NEW/ $REF/"
    #echo "-- $CMD"; $CMD
    #exit
#fi

#if [ "$1" = "-all" ]; then
    #CMD="diff -r $NEW/ $REF/"
    #echo "-- $CMD"; $CMD
    #exit
#fi

HIGH_LEVEL_DIFF() {
    #CMD="diff -rq ~/labs/tf-gen.2024-jun/ ~/src/mjbright.tf-scenarios/Solutions/tf-gen/2024-jun/"
    CMD="diff -rq $NEW/ $REF/"

    echo "-- $CMD"
    read -p "Press enter ..." DUMMY; [ "${DUMMY,,}" = "q" ] && exit 0
    $CMD | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak" 
}

DETAILED_DIFF() {
    CMD="diff -r $NEW/ $REF/"
    echo "-- $CMD"
    read -p "Press enter ..." DUMMY; [ "${DUMMY,,}" = "q" ] && exit 0
    $CMD | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak" 
}

HIGH_LEVEL_DIFF
DETAILED_DIFF

#DIFF_REF_FILES=$( diff -rq $NEW/ $REF/ | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak" | grep " differ$" | sed -e 's/^Files //' -e 's/ and .*//' | sed "s?$REF/??" )
DIFF_REF_FILES=$( diff -rq $NEW/ $REF/ | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak" | grep " differ$" | sed -e 's/^Files //' -e 's/ and .*//' | sed "s?$NEW/??" )
# diff -rq ~/labs/tf-gen.2024-jun/ ~/src/mjbright.tf-scenarios/Solutions/tf-gen/2024-jun/ | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak"  | grep " differ$" | sed -e 's/^Files //' -e 's/ and .*//' | sed "s?$REF/??"
# diff -rq $NEW/ $REF/ | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak"  | grep " differ$" | sed -e 's/^Files //' -e 's/ and .*//' | sed "s?$NEW/??"

echo; echo "Changed files (deemed important):"
diff -rq $NEW/ $REF/ | grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak"  | grep " differ$" | sed -e 's/^Files //' -e 's/ and .*//' | sed "s?$NEW/??"

#echo NEW=$NEW
#exit

echo
echo "About to merge changes into $REF/ ..."
read -p "Press enter ..." DUMMY; [ "${DUMMY,,}" = "q" ] && exit 0
for REF_FILE in $DIFF_REF_FILES; do
    echo "REF_FILE=$REF_FILE"
#exit

    echo; echo "-- diff $NEW/$REF_FILE $REF/$REF_FILE"
    read -p "Press enter ..." DUMMY; [ "${DUMMY,,}" = "q" ] && exit 0
    [ "${DUMMY,,}" = "s" ] && continue
    diff $NEW/$REF_FILE $REF/$REF_FILE

    read -p "Copy (left) NEW file to (right) REF file ? (type 'yes') ... " YES
    if [ "${YES,,}" = "yes" ]; then
        echo cp -a $NEW/$REF_FILE $REF/$REF_FILE
        cp -a $NEW/$REF_FILE $REF/$REF_FILE
    fi
done


#diff -rq ~/labs/tf-gen.2024-jun/ ~/src/mjbright.tf-scenarios/Solutions/tf-gen/2024-jun/ |
    #grep -vE "terraform.tfstate|.terraform.lock.hcl|.unused$|.bak" 

