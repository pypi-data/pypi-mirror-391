#!/bin/bash

gtf_file="/mnt/data1/ref/gencode/v49/human/gencode.v49.annotation.gtf.gz"

../.venv/bin/python ../main.py \
    -e chr16:89722829-89728948 \
    -p 10 \
    -r ${gtf_file} \
    --density samples.bam.tsv \
    --output test.v051.pdf \
    --width 6 \
    --height 3 \
    --same-y \
    --sites 89724829,89726948 \
    --intron-scale 0.05


# /home/TW/anaconda3/envs/trackplot_v0.5.3/bin/trackplot \
#     -e chr16:89722829-89728948 \
#     -p 10 \
#     -r ${gtf_file} \
#     --density samples.bam.tsv \
#     --output test.v053.pdf \
#     --width 6 \
#     --height 3 \
#     --same-y \
#     --sites 89724829,89726948 \
#     --intron-scale 0.05


../.venv/bin/python ../main.py \
    -e chr16:89722829-89728948 \
    -p 10 \
    -r ${gtf_file} \
    --density samples.bam.tsv \
    --output test.v053.included_junctions.png \
    --width 6 \
    --height 3 \
    --same-y \
    --sites 89724829,89726948 \
    --intron-scale 0.05 \
    --included-junctions chr16:89724829-89726948 