import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping, Union

logger = logging.getLogger(f"{__name__}.abpackingangle")


class AbPackingAngle:
    """ Python wrapper of the abpackingangle binary """

    def __init__(self,
                 binary_path: Path):
        """
        Initializes the Python abpackingangle wrapper.

        Args:
            binary_path: (str) The path to the abpackingangle executable.
        Raises:
            RuntimeError: If abpackingangle binary or database not found within the path.
        """
        self.binary_path = binary_path

    @staticmethod
    def _get_file_name(input_file_path: str):
        a, _ = os.path.splitext(os.path.basename(input_file_path))
        return a

    def query(self, pdb_path: Path) -> Mapping[str, Any]:
        """
        abpackingangle V2.1 (c) 2007-2019, UCL, Abhi Raghavan and Andrew Martin

        Usage: abpackingangle [-p pdbcode][-o vecfile][-v][-q][-d][-f] [in.pdb [out.txt]]
                   -p Specify a PDB code to be printed with the results
                   -o Create a PDB file containing the vectors used for angle calculations
                   -v Verbose
                   -q Quiet - prints only the angle
                   -d Print the distance between centroids as well as the angle
                   -f Force angle calculation even when centroid distance > 25.000000

        abpackingangle calculates the packing angle between VH and VL domains
        as described by Abhinandan and Martin 23(2010),689-697.

        Args:
            pdb_path: antibody pdb file path
        """
        pdb_fn = pdb_path.stem

        cmd = [self.binary_path.as_posix(), '-v', '-d']
        cmd += [pdb_path.as_posix()]

        logger.info('Launching subprocess "%s"', ' '.join(cmd))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if retcode := process.wait():
            # Logs have a 15k character limit, so log abpackingangle error line by line.
            logger.error('abpackingangle failed. abpackingangle stderr begin:')
            for error_line in stderr.decode('utf-8').splitlines():
                if error_line.strip():
                    logger.error(error_line.strip())
            logger.error('abpackingangle stderr end')
            raise RuntimeError('abpackingangle failed\nstdout:\n%s\n\nstderr:\n%s\n' % (
                stdout.decode('utf-8'), stderr[:500_000].decode('utf-8')))

        abpackingangle_text = stdout.decode('latin')

        return dict(pdb=pdb_fn, abpackingangle_text=abpackingangle_text, 
                    stderr=stderr)
