#!/bin/bash
#

IPFILE=""

MAX_LINE_LEN=80
LEFT_COLS=7

while [ ! -z "$1" ]; do
    case $1 in
        -m) shift; MAX_LINE_LEN=$1;;
         *) IPFILE=$1;;
    esac
    shift
done

let MAX=MAX_LINE_LEN+LEFT_COLS

# CAT input file with line numbers:
# - if/cat: cat input file or stdin, with line numbers
#           also sanitize output (control chars can mess up terminal colours)
# - cut: select first columns with line number and columns after MAX_LINE_LEN chars
# - grep: Remove lines with no extra chars (after column 80 of input file)
#         By detecting lines with initial spaces, line number and then a TAB then end of line

if [ ! -z "$IPFILE" ]; then
    cat -vn $IPFILE
else
    cat -vn
fi |
    cut -c 1-${LEFT_COLS},${MAX}-5000 |
    grep -v "^ *[0-9]*"$'\t'"$"

