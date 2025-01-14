#!/bin/bash

files=`ls $1`
cd ./../..

for file in $files;
do
    sbatch $1/$file
done
