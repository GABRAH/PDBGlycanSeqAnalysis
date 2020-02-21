#!/usr/bin/env bash

for fullpath in /home/harold/Dev/wurcsTestAlpha/structures/*; do
    if [ -d ${fullpath} ]; then
    dirname=$(basename ${fullpath})
    rm -rf /home/harold/Dev/wurcsTestAlpha/results/offline/${dirname}/privateer_output/
        for file in ${fullpath}/*.pdb; do
            id=$(basename -s .pdb ${file})
            newdirectory="/home/harold/Dev/wurcsTestAlpha/results/offline/${dirname}/privateer_output/${id}"
            if [ ! -d ${newdirectory} ]; then
                mkdir -p ${newdirectory}
                (cd ${newdirectory} && "/home/harold/Dev/privateer/./privateer" -pdbin ${file})
            fi
        done
    fi
done

