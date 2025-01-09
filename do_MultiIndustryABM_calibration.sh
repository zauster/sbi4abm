#!/usr/bin/env sh
set -u
nsims=${1:-"500x2"}
# output_dir=${2:-"results_artificial"}
output_dir=${2:-"results_empirical"}
method=${3:-"maf_gru"}
nworker=${4:-10}
nsamples=${5:-10000}

## Script for killing juliaclient zombie threads:
# ./kill_jc_crashed.sh > kill_jc.log &

## activates the python environment
source venv_sbi4abm/bin/activate

echo "=> Running the sbi4abm algorithm"
python sbi4abm/utils/job_script.py \
    --task=MultiIndustryABM \
    --method=${method} \
    --outloc=${output_dir} \
    --nsims=${nsims} \
    --nw=${nworker} \
    --nsamples=${nsamples}

## deactivate python environment
deactivate

## Kill the kill script:
# cat /tmp/kill_jc_crashed.pid | xargs kill
