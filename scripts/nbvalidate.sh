#!/usr/bin/env bash

INSTALL_NBTK() {
    python3 -m venv ~/.venv/nbtoolbelt
    . ~/.venv/nbtoolbelt/bin/activate
    pip install -U upgrade
    pip install pip -U upgrade
    pip install nbtoolbelt
}

#INSTALL_NBTK

. ~/.venv/nbtoolbelt/bin/activate
nbtb validate -v $*

#nbtb validate ~/src/mjbright.labs-terraform-private/tf-intro/FULL_NOTEBOOK/FULL.ipynb -v

