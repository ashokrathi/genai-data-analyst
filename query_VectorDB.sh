#!/bin/bash
cmd="python src/vectorDB/pineconeDB.py -query \"$1\""
echo "Executing: $cmd ..."
eval $cmd
