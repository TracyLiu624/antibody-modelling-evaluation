#!/bin/zsh

# this assumes you are running under path:
# `antibody-cdr-modelling-evaluation/scripts/run_profit_abpackingangle`

# abymod 
python main.py \
  --model_method abymod \
  --config main.yaml \
  --model_dir ../../data/model/abymod \
  --out_dir ../../results/

# abymod 
python main.py \
  --model_method lyra \
  --config main.yaml \
  --model_dir ../../data/model/lyra \
  --out_dir ../../results/

# igfold
python main.py \
  --model_method igfold \
  --config main.yaml \
  --model_dir ../../data/model/igfold \
  --out_dir ../../results/

# rosetta antibody 
python main.py \
  --model_method RosettaAntibody \
  --config main.yaml \
  --model_dir ../../data/model/RosettaAntibody \
  --out_dir ../../results/