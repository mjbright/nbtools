
cd $( dirname $0 )

python -m py_compile ./nbtool.py &&
    echo -e "\n\tCompilation OK" ||
    echo -e "\n\tCompilation failed"


