# Antibody Modelling Evaluation

## Introduction

This repository contains the code we used to evaluate:
- antibody Complementarity Determining Region (CDR) structure prediction, and 
- VH/VL packing angle prediction 

using some of the commonly used methods including [abYmod](http://abymod.abysis.org), [lyra](https://services.healthtech.dtu.dk/services/LYRA-1.0/), [RosettaAntibody](https://new.rosettacommons.org/demos/latest/tutorials/install_build/install_build), [IgFold](https://github.com/Graylab/IgFold)

## Usage

We evaluate the four methods on a list of non-redundant set of antibody structures (`data/abdbids.txt` a list of AbDb IDs) collected from the AbDb database. 

Evaluation includes **local** and **global** fitting CαRMSD of the CDR loops and VH/VL domain packing angle of the predicted antibody structures against the native antibody structures.

**Global fitting** is performed by first fitting the framework region of the predicted antibody onto that of the native antibody, then calculate the CαRMSD of the CDR loops, reflecting the similarity of CDR orientation relative to the framework region between the predicted and native antibody structures. 
**Local fitting** is performed by fitting the predicted CDR loops onto the native CDR loops directly, without fitting the framework region first, reflecting the shape similarity of the CDR loops.

### Dependencies
Before running our evaluation code, please make sure you have the following dependency packages installed, used the link below for download and installation instructions
- [ProFit](http://www.bioinf.org.uk/servers/profit/): a package for protein structure superposition and fitting
- [abpackingangle](https://github.com/ACRMGroup/abpackingangle): a package for calculating VH/VL domain packing angle 

### Prepare a conda environment
Create a conda env and install the utilities provided in `cdr_eval` required for the evaluation. 
```
$ conda create -n cdr_eval 
$ conda activate cdr_eval
$ cd /path/to/antibody-cdr-modelling-evaluation 
$ pip install -e . 
```

### Run the evaluation
Run the evaluation shell script `main.sh` provided under `scripts/run_eval` with the following arguments
```
$ cd scripts/run_eval
# you might need to grant the script execution permission
$ chmod +x main.sh
$ ./main.sh 
```
`main.sh` runs the evaluation on the four methods on an example antibody structure `1a6u_0` which is a free antibody structure (meaning on its own wihtout the antigen structure). The evaluation results are output in `results` directory grouped by method names.

- `main.yaml`: configuration file for `main.py`, paths are relative to this repo root directory
  - `abdb`: path pointing to the native antibody structures in AbDb database
  - `profit`: this is the executable path for ProFit, you might have a different path depending on your installation than the one provided in the config file
  - `abpackingangle`: this is the executable path for abpackingangle, again, you might have a different path depending on your installation than the one provided in the config file
  - `profit_local_fitting`: this is the ProFit script for **local** fitting of the CDR loops, we encourage users to refer to ProFit documentation for detailed usage and explanation of the script
  - `profit_global_fitting`: this is the ProFit script for **global** fitting of the CDR loops, we encourage users to refer to ProFit documentation for detailed usage and explanation of the script

- `main.py`: main script for running the evaluation, it takes the following arguments
  - `--config`: path to the config file `main.yaml`
  - `--method_method`: method name, one of `abymod`, `lyra`, `igfold`, `RosettaAntibody`
  - `--model_dir`: path to the directory containing the predicted CDR structures
  - `out_dir`: path to the output directory for the evaluation results

### Example evaluation result JSON file (e.g. `results/abymod/1a6u_0.json`):
```json
{
    "abdb_id": "1a6u_0"
    "abdb_angle": -46.673304,
    "model_angle": -46.332774,
    "rmsd": [0.202, 0.183, 0.212, 0.225, 0.11, 0.311, 0.53, 0.495, 0.437, 0.494, 0.326, 0.304, 0.307, 0.599],
    "cdr": ["H1", "H2", "H3", "L1", "L2", "L3", "HFR", "H1", "H2", "H3", "LFR", "L1", "L2", "L3"],
    "fitting": ["local", "local", "local", "local", "local", "local", "global", "global", "global", "global", "global", "global", "global", "global"],
}
```
- `abdb_angle`: VH/VL domain packing angle of the native antibody structure
- `model_angle`: VH/VL domain packing angle of the predicted antibody structure
- `rmsd`: CαRMSD of the CDR loops
- `cdr`: CDR loop names, same length as `rmsd`, indicating which CDR loop the CαRMSD value corresponds to 
- `fitting`: fitting type, either `local` or `global`. Same length as `rmsd`, indicating which fitting type the CαRMSD value corresponds to.
  - `global`: CDR loop fitting using ProFit **global** fitting script, which calculates the CαRMSD of a CDR loop by fitting the framework region of the predicted antibody onto that of the native structure first, then calculate CDR loop CαRMSD, e.g. to calculate the global CαRMSD of H1 loop, we first fit the VH framework region of the predicted antibody onto the native antibody, then calculate the CαRMSD of the H1 loop.
  - `local`: CDR loop fitting using ProFit **local** fitting script, which calculates the CαRMSD of a CDR loop by fitting the predicted CDR loop onto the native CDR loop directly, without fitting the framework region first, e.g. to calculate the local CαRMSD of H1 loop, we fit the predicted H1 loop onto the native H1 loop directly.