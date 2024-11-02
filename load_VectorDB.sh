#!/bin/bash
ROOT_FOLDER=$(cd `dirname $0`; pwd)
echo "App Root Folder: $ROOT_FOLDER"
cd "$ROOT_FOLDER"

datasets="Sales World_Top_Companies"
if [ $# -ge 1 ]; then
    datasets="$1"
fi
echo "datasets to load: $datasets"

for d in $datasets
do
    cmd="python src/vectorDB/pineconeDB.py -load $d"
    echo "Executing: $cmd ..."
    eval $cmd
done
