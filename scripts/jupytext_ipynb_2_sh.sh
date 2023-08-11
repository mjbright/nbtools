
if [ -d "$1" ]; then
    cd "$1"
    pwd
fi

echo "converting README.ipynb to README.sh (percent format):"
CMD="jupytext --to sh:percent README.ipynb"
echo "-- $CMD"; $CMD
ls -altr README.ipynb  README.sh

## # ALL:
## JT_OPT="--opt notebook_metadata_filter=all"
## CMD="jupytext $JT_OPT --to sh:percent README.ipynb -o README.all.sh"
## echo "-- $CMD"; $CMD

echo "Configuring README.ipynb for pairing:"
#CMD="jupytext --set-formats ipynb,py:percent README.ipynb"
CMD="jupytext --set-formats ipynb,sh:percent README.ipynb"
echo "-- $CMD"; $CMD


