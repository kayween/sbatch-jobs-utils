#!/bin/bash

files=`ls $1`

for file in $files;
do
    sbatch $1/$file
done
