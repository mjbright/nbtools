#!/usr/bin/env bash

./nbjoin.py \
    -op ~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL.ipynb \
    \
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

