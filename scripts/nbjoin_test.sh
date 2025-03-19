#!/usr/bin/env bash

./nbjoin.py \
    -op ~/src/mjbright.labs-terraform-private/tf-intro/FULL.ipynb \
    \
    -of NBJOIN_HEADER_FOOTER/FOOTER.ipynb \
    -oh NBJOIN_HEADER_FOOTER/HEADER.ipynb \
    \
    NBJOIN_TEST/IP_TF_Lab1.ipynb \
    NBJOIN_TEST/IP_TF_Lab2.Workflow.ipynb \
    NBJOIN_TEST/IP_TF_Lab3.ipynb \
    NBJOIN_TEST/IP_TF_Lab4.ControlStructures.ipynb \
    NBJOIN_TEST/IP_TF_Lab5.ipynb \
    NBJOIN_TEST/IP_TF_Lab7.Modules.ipynb \
    NBJOIN_TEST/IP_TF_Lab8.Import.ipynb \
    NBJOIN_TEST/IP_TF_Lab10.Revision.ipynb \

