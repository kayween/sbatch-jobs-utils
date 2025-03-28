#!/bin/bash

files=`ls $1`

currentdir=$PWD
parentdir="$(dirname "$PWD")"
cd ..

for file in $files
do
    bash $currentdir/$1/$file
done

