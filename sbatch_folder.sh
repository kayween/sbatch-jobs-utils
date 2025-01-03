#!/bin/bash

files=`ls $1`

for ii in $files;
do
    bash $1/$ii
done
