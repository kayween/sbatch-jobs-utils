#!/bin/bash

files=`ls $1`

for ii in $files;
do
  sbatch $1/$ii
done
