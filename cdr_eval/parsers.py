import logging
import re
from typing import Union
from typing import Dict, Tuple

from Bio.SeqUtils import IUPACData

# aa letters mapping between 1 and 3
AA_3to1: Dict[str, str] = {k.upper(): v for k, v in IUPACData.protein_letters_3to1.items()}
AA_3to1_EXT: Dict[str, str] = {k.upper(): v for k, v in IUPACData.protein_letters_3to1_extended.items()}

logger = logging.getLogger(f'{__name__}.parser')


def profit_parser(text: str,
                  pairdist: bool = False):
    """
    Args:
        pairdist:
        text: (str) ProFit output text

    Returns:
        results: (dict) keys: rmsd and num_atm_aln => rmsd over FrameWork (FR), L1, L2, L3, H1, H2, H3 regions
    """
    results = dict(rmsd=[], num_atm_aln=[])

    try:
        assert text.count('RMS:') == 15
    except AssertionError:
        raise ValueError(f"ProFit output parsing error: {16 - text.count('RMS:')} regions fitting failed.")

    rms_reg = re.compile(r'RMS: ([\d.]+)')
    num_atm_reg = re.compile(r'Number of fitted atoms: (\d+)')
    dis_reg = re.compile(r'Dist: ([\d.]+)')
    dis_reg_long = re.compile(r'\s*([HL])\s+([\dA-Z]+)\s+([A-Z]{3})\s+([A-Z]+)\s+:'
                              r'\s*([HL])\s+([\dA-Z]+)\s+([A-Z]{3})\s+([A-Z]+)\s+'
                              r'Dist: ([\d.]+)')

    # rms
    rms = [float(i) for i in
           rms_reg.findall(text)]  # HL.fr, h1, h2, h3, l1, l2, l3, h.fr, h_h1, h_h2, h_h3, l.fr, l_l1, l_l2, l_l3
    # num_atm_aln
    num_atm_aln = [int(i) for i in num_atm_reg.findall(text)]  # HL.fr, H.fr, L.fr
    bs = [b for b in text.split('RMS:') if 'Dist: ' in b]
    num_atm_aln += [b.count('Dist') for b in bs[:6]]  # + h_h1, h_h2, h_h3, l_l1, l_l2, l_l3

    # add to results
    results['rmsd'].extend(rms)
    results['num_atm_aln'].extend(num_atm_aln)

    return results


def profit_parser_cdr_local_rmsd(text: str,
                                 pairdist: bool = False):
    """
    Args:
        pairdist:
        text: (str) ProFit output text

    Returns:
        results: (dict) keys: rmsd and num_atm_aln => rmsd over FrameWork (FR), L1, L2, L3, H1, H2, H3 regions
    """
    results = dict(region=[], rmsd=[], num_atm_aln=[])

    NUM_RMS = 6
    try:
        assert text.count('RMS:') == NUM_RMS
    except AssertionError as e:
        raise ValueError(
            f"ProFit output parsing error: {NUM_RMS - text.count('RMS:')} regions fitting failed."
        ) from e

    rms_reg = re.compile(r'RMS: ([\d.]+)')
    num_atm_reg = re.compile(r'Number of fitted atoms: (\d+)')
    dis_reg = re.compile(r'Dist: ([\d.]+)')
    dis_reg_long = re.compile(r'\s*([HL])\s+([\dA-Z]+)\s+([A-Z]{3})\s+([A-Z]+)\s+:'
                              r'\s*([HL])\s+([\dA-Z]+)\s+([A-Z]{3})\s+([A-Z]+)\s+'
                              r'Dist: ([\d.]+)')

    # rms & num_atm_aln
    rms = [float(i) for i in rms_reg.findall(text)]  # H1, H2, H3, L1, L2, L3
    num_atm_aln = [int(i) for i in num_atm_reg.findall(text)]  # H1, H2, H3, L1, L2, L3

    # add to results
    results['rmsd'].extend(rms)
    results['num_atm_aln'].extend(num_atm_aln)

    return results


def abpackingangle_parser(text: str) -> Union[float, bool]:
    """
    abpackingangle -v -d ~/Dataset/AbDb/LH_Combined_Chothia/5MU0_2.pdb

    Light chain centroid:           41.372500       -27.248500      -10.787625
    Light chain projection:         46.039597       -25.517011      -11.799863
    Heavy chain centroid:           42.401750       -25.976875      4.139750
    Heavy chain projection:         46.855832       -28.134762      4.880031

    Distance:  15.017   Packing angle: -47.682785

    Args:
        text: (str) abpackingangle output text

    Returns:
        results: (dict) keys: rmsd and num_atm_aln => rmsd over FrameWork (FR), L1, L2, L3, H1, H2, H3 regions
    """
    angle = None

    try:
        angle = float(re.search(r"Packing angle: ([-\d]+\.\d+)", text)[1])
    except Exception as e:
        logger.error(e)
        logger.error(text)
        logger.error("abpackingangle matching failed.")

    return angle

