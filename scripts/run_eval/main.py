# basic
import re
import json
import yaml
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
# custom 
import cdr_eval
from cdr_eval.abpackingangle import AbPackingAngle
from cdr_eval.parsers import abpackingangle_parser
from cdr_eval.profit import ProFit
from cdr_eval.logger import setup_logger

# repo root
REPO_ROOT = Path(cdr_eval.__file__).parents[1]


# ==================== Function ====================
def profit_local_fitting_parser(profit_text: str) -> Optional[Dict[str, float]]:
    """
    If running okay, profit_text should give 6 RMS values

    Args:
        profit_text: (str) output from ProFit running profit-local-fitting script

    Returns:
        rmsd: (Dict[str, float]) keys are CDRs, values are rmsd values
    """
    region = ["H1", "H2", "H3", "L1", "L2", "L3"]
    rmsd = [float(i) for i in re.findall(r"RMS: ([\d.]+)", profit_text)]
    try:
        assert len(rmsd) == 6
    except AssertionError:
        logger.error(f"Insufficient RMSD values to unpack. Expected 6, got {len(rmsd)}")
        return None

    rmsd = dict(zip(region, rmsd))
    return rmsd


def profit_global_fitting_parser(profit_text: str) -> Optional[Dict[str, float]]:
    """
    If running okay, profit_text should give 8 RMS values - HFR, H1, H2, H3, LFR, L1, L2, L3

    Args:
        profit_text: (str) output from ProFit running profit-global-fitting script

    Returns:
        rmsd: (Dict[str, float]) keys are CDRs, values are rmsd values
    """
    region = ["HFR", "H1", "H2", "H3", "LFR", "L1", "L2", "L3"]
    rmsd = [float(i) for i in re.findall(r"RMS: ([\d.]+)", profit_text)]
    try:
        assert len(rmsd) == 8
    except AssertionError:
        logger.error(f"Insufficient RMSD values to unpack. Expected 8, got {len(rmsd)}")
        return None

    rmsd = dict(zip(region, rmsd))
    return rmsd


def gen_file_map(abdb_fps: List[Path], model_dir: Path) -> pd.DataFrame:
    d = {
        "abdbid": [re.search(r"pdb([A-Za-z\d]{4}_\d+[A-Z]*)\.cho", fp.name)[1] for fp in abdb_fps],
        "abdb_fp": abdb_fps,
    }
    d["model_fps"] = [
        list(model_dir.glob(f"{abdbid}*"))[0] for abdbid in d["abdbid"]
    ]
    # to DataFrame
    return pd.DataFrame(d)


# input
def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, help="config file path")
    # mutable args
    parser.add_argument("--model_method", type=str, help="modelling method e.g. abymod", required=True)
    parser.add_argument("--model_dir", type=str, help="model file directory", required=True)
    parser.add_argument("--out_dir", type=str, help="output directory", required=True)

    args = parser.parse_args()
    config_fp = args.config
    model_method = args.model_method
    model_dir = Path(args.model_dir)
    out_dir = Path(args.out_dir)
    with open(config_fp, 'r') as f:
        cfg = yaml.safe_load(f)

    _add_repo_root_to_path = lambda k1, k2: cfg[k1].update({k2: REPO_ROOT.joinpath(cfg[k1][k2])})
    _convert2path = lambda k1, k2: cfg[k1].update({k2: Path(cfg[k1][k2])})
    
    _add_repo_root_to_path("dataset", "abdb")
    _add_repo_root_to_path("pre-defined-process", "profit_local_fitting")
    _add_repo_root_to_path("pre-defined-process", "profit_global_fitting")
    _convert2path("executable", "profit")
    _convert2path("executable", "abpackingangle")
    
    return cfg, model_method, model_dir, out_dir


# ==================== Main ====================
if __name__ == "__main__":
    config, model_method, model_dir, out_dir = cli()

    # ensure output and log dir exist
    out_dir = out_dir.joinpath(model_method)
    log_dir = out_dir.joinpath("log")
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    # logger
    logger = setup_logger(save_dir=log_dir,
                          info_file_name="run_profit_abpackingangle.log",
                          err_file_name="run_profit_abpackingangle.err",
                          time_stamp=True)

    # Runner
    abpa_runner = AbPackingAngle(binary_path=config["executable"]["abpackingangle"])
    profit_local_runner = ProFit(binary_path=config["executable"]["profit"],
                                 profit_script_file_path=config["pre-defined-process"]["profit_local_fitting"])
    profit_global_runner = ProFit(binary_path=config["executable"]["profit"],
                                  profit_script_file_path=config["pre-defined-process"]["profit_global_fitting"])

    # File maps: model vs true structure
    df = gen_file_map(abdb_fps=list(config["dataset"]["abdb"].glob("*.cho")),
                      model_dir=model_dir)

    # run fitting and abpackingangle
    for abdbid, abdb_fp, model_fp in df.values:
        # log start
        logger.info(f"{abdbid} Start")
        result = {
            "abdb_angle": None,
            "model_angle": None,
            "cdr": [],
            "rmsd": [],
            "fitting": [],
            "abdb_id": abdbid,
        }
        # ======== abpacking angle ========
        # ground-truth
        try:
            raw_output = abpa_runner.query(pdb_path=abdb_fp)
            angle = abpackingangle_parser(text=raw_output["abpackingangle_text"])
            if angle is not None:
                result["abdb_angle"] = float(angle)
        except Exception as e:
            logger.error(f"{abdbid} abdb file: Getting angle FAILED.\nError info:\n{e}")

        # model
        try:
            raw_output = abpa_runner.query(pdb_path=model_fp)
            angle = abpackingangle_parser(text=raw_output["abpackingangle_text"])
            if angle is not None:
                result["model_angle"] = float(angle)
        except Exception as e:
            logger.error(f"{abdbid} {model_method} file:  Getting angle FAILED.\nError info:\n{e}")

        # ======== ProFit local fitting ========
        try:
            raw_output = profit_local_runner.query(ref_pdb_path=abdb_fp,
                                                   mob_pdb_path=model_fp)
            d = profit_local_fitting_parser(profit_text=raw_output["results"])
            if d is not None:
                for k, v in d.items():
                    result["cdr"].append(k)
                    result["rmsd"].append(v)
                    result["fitting"].append('local')
        except Exception as e:
            logger.error(f"{abdbid} Local fitting FAILED.\nError info:\n{e}")

        # ======== ProFit global fitting ========
        try:
            raw_output = profit_global_runner.query(ref_pdb_path=abdb_fp,
                                                    mob_pdb_path=model_fp)
            d = profit_global_fitting_parser(profit_text=raw_output["results"])
            if d is not None:
                for k, v in d.items():
                    result["cdr"].append(k)
                    result["rmsd"].append(v)
                    result["fitting"].append("global")
        except Exception as e:
            logger.error(f"{abdbid} Global fitting FAILED.\nError info:\n{e}")

        # save to local
        out_fp = out_dir.joinpath(f"{abdbid}.json")
        with open(out_fp, "w") as f:
            json.dump(result, f, indent=4)

        logger.info(f"{abdbid} End\n\n")
