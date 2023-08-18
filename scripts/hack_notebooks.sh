#!/bin/bash

# 1869  2023-08-11 19:03:16for FILE in ../[1-9].*/*.{sh,ipynb,md}; do echo "---- $FILE"; sed -i.bak -e 's/R_DOCKER/__R_DOCKER/g' -e 's/R_CURL/__R_CURL/g' -e 's/EXCL_FN/_/g' -e 's/TF_/__TF_/g' $FILE; done

DANGEROUS
exit

cd ~/src/mjbright.tf-scenarios-private/ServeUpLabs/content/azure/

for FILE in ./[1-9].*/*.{sh,ipynb,md}; do
    echo "---- $FILE"
    sed -i.bak \
        -e 's/__R_DOCKER/__DOCKER/g' \
        -e 's/__R_CURL/__CURL/g' \
        $FILE
    #sed -i.bak \
    #    -e 's/R_DOCKER/__R_DOCKER/g' \
    #    -e 's/R_CURL/__R_CURL/g' \
    #    -e 's/EXCL_FN/_/g' \
    #    -e 's/TF_/__TF_/g' \
    #   $FILE
done

