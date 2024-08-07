#!/usr/bin/env sh
set -u
nsims=${1:-"300x2"}
nworker=${2:-10}
output_dir=${3:-"results_artificial"}

#./kill_jc_crashed.sh > kill_jc.log &
source venv_sbi4abm/bin/activate

# mlp, nsf do not work
# embedding=elman did not produce good results

# for network in maf made
for network in maf made resnet mlp
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
deactivate
