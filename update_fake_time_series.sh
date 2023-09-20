#!/usr/bin/env sh

echo "=> Producing fake time series"
juliaclient \
    --project=/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/Calibration \
    /mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/Calibration/src/run_one_simulation.jl \
    --config_file=/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/model_config.toml \
    --output_dir=test \
    --random_seed=12345

echo "=> Extracting and writing to sbi4abm directory"
cd R
python 01_extract_fake_obs.py
cd ..
