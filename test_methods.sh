#!/usr/bin/env sh
set -u
nsims=${1:-"500x5"}
output_dir=${2:-"results"}

./kill_jc_crashed.sh > kill_jc.log &

# nsf does not work

for network in maf mdn made resnet mlp
# for network in mlp
do
    for embedding in gru elman
    do
        echo "\n=> Testing ${network}_${embedding}"
        python sbi4abm/utils/job_script.py \
            --task MultiIndustryABM \
            --method ${network}_${embedding} \
            --outloc ${output_dir} \
            --nsims ${nsims} \
            --nw 10
    done
done

# --task mvgbm \

cat /tmp/kill_jc_crashed.pid | xargs kill
