#!/usr/bin/env sh
set -u
nsims=${1:-"500x3"}
nworker=${2:-10}
output_dir=${3:-"results"}

#./kill_jc_crashed.sh > kill_jc.log &
# source venv_sbi4abm/bin/activate

# mlp, nsf do not work
# embedding=elman did not produce good results

# for network in maf made resnet mlp
for network in maf made
do
    for embedding in gru
    do
        echo -e "\n=> Testing ${network}_${embedding}"
        python sbi4abm/utils/job_script.py \
            --task MultiIndustryABM \
            --method ${network}_${embedding} \
            --outloc ${output_dir} \
            --nsims ${nsims} \
            --nw ${nworker}
    done
done

# cat /tmp/kill_jc_crashed.pid | xargs kill
# deactivate
