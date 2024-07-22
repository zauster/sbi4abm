#!/usr/bin/env sh

## Script for killing juliaclient zombie threads:
# ./kill_jc_crashed.sh > kill_jc.log &

## activates the python environment
source venv_sbi4abm/bin/activate

echo "=> Running the sbi4abm algorithm"
python sbi4abm/utils/job_script.py \
    --task=MultiIndustryABM \
    --method=resnet_gru \
    --outloc=results \
    --nsims=50x1 \
    --nw=10

## deactivate python environment
deactivate

## Kill the kill script:
# cat /tmp/kill_jc_crashed.pid | xargs kill
