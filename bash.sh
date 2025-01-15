#!/bin/bash

files=`ls $1`

for file in $files;
do
    bash $1/$file
done

