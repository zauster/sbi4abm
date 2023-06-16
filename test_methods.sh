#!/usr/bin/env sh
set -u
nsims=${1:-"100x5"}
output_dir=${2:-"results"}

for embedding in gru ##elman
do
    for network in maf ##mdn nsf made
    do
        echo "\\n=> Testing ${network}_${embedding}"
        python sbi4abm/utils/job_script.py --task mvgbm --method ${network}_${embedding} --outloc ${output_dir} --nsims ${nsims}
    done
done
