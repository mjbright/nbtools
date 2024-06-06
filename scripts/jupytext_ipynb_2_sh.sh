
IPYNB=README.ipynb

if [ -d "$1" ]; then
    cd "$1"
    pwd
    shift
fi

case "$1" in
    *.ipynb) IPYNB=$1; shift;;
esac

IPYNB_SH=${IPYNB%.ipynb}.sh

echo "converting $IPYNB to ${IPYNB_SH} (percent format):"
CMD="jupytext --to sh:percent $IPYNB"
echo "-- $CMD"; $CMD
ls -altr $IPYNB  ${IPYNB_SH}

## # ALL:
## JT_OPT="--opt notebook_metadata_filter=all"
## CMD="jupytext $JT_OPT --to sh:percent $IPYNB -o ${IPYNB_SH}"
## echo "-- $CMD"; $CMD

echo "Configuring $IPYNB for pairing:"
#CMD="jupytext --set-formats ipynb,py:percent $IPYNB"
CMD="jupytext --set-formats ipynb,sh:percent $IPYNB"
echo "-- $CMD"; $CMD


