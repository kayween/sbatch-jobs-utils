#!/bin/bash

files=`ls $1`
cd ./../..

for file in $files;
do
    bash $1/$file
done

