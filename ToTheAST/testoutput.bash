#!/bin/bash

parser="python3 $PWD/scanner.py"
graphvis="python2 $PWD/parse-tree-to-graphvis.py"
dot="dot -Tpng -o "

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 testdir outdir"
    exit 1
fi

if [ ! -d "$2" ]
then mkdir "$2"; fi

for file in $(ls $1)
do
    absfile="$PWD/$1/$file"
    if [ ! -d "$2/$file" ]; then mkdir "$2/$file"; fi
    pushd "$2/$file" > /dev/null
        # echo "Parsing $absfile"
        # echo "$parser < $absfile"
        cp $absfile .
        $parser < $absfile
        cat OUTPUT.p | $graphvis | $dot parsetree.png
        cat OUTPUT.a | $graphvis | $dot arithmetictree.png
        # echo "Done parsing"
    popd > /dev/null
done
