#!/usr/bin/env bash

OP=~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL.ipynb

die() { echo "$0: die - $*" >2; exit 1; }

python3 -m py_compile   nbjoin.py || die "Syntax error"

set -x
./nbjoin.py -nbtool -oN -op $OP \
    -oh ~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL_HEADER.ipynb \
    -of ~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL_FOOTER.ipynb \
    \
    NBJOIN_TEST/IP_TF_Lab1.ipynb \
    NBJOIN_TEST/IP_TF_Lab2.Workflow.ipynb \
    NBJOIN_TEST/IP_TF_Lab3.ipynb \
    NBJOIN_TEST/IP_TF_Lab4.ControlStructures.ipynb \
    NBJOIN_TEST/IP_TF_Lab5.ipynb \
    NBJOIN_TEST/IP_TF_Lab7.Modules.ipynb \
    NBJOIN_TEST/IP_TF_Lab8.Import.ipynb \
    NBJOIN_TEST/IP_TF_Lab10.Revision.ipynb \

set +x

echo
~/.venv/nbtoolbelt/bin/nbtb validate $OP -v

echo
./nbcheck.py $OP
echo
./nbcheck.py ${OP%.ipynb}.multiline.ipynb

