#!/bin/bash

ROOT_FOLDER=$(cd `dirname $0`; pwd)
echo "App Root Folder: $ROOT_FOLDER"
cd "$ROOT_FOLDER"
streamlit run src/app.py
