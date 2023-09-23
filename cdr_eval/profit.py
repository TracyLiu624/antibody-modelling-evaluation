import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Mapping, Union, Dict

logger = logging.getLogger(f"{__name__}.profit")


class ProFit:
    """Python wrapper of the ProFit binary."""

    def __init__(self,
                 binary_path: Path,
                 profit_script_file_path: Path):
        """
        Initializes the Python ProFit wrapper.

        Args:
            binary_path: (str) The path to the ProFit executable.
            profit_script_file_path: (str) a text file of profit commands
        Raises:
            RuntimeError: If ProFit binary or database not found within the path.
        """
        self.binary_path = binary_path
        self.profit_script_file_path = profit_script_file_path

    @staticmethod
    def _get_file_name(input_file_path: str):
        a, _ = os.path.splitext(os.path.basename(input_file_path))
        return a

    def query(self,
              ref_pdb_path: Path,
              mob_pdb_path: Path) -> Dict[str, str]:
        """

        Args:
            ref_pdb_path: reference pdb file path
            mob_pdb_path: mobile pdb file path
        """
        ref_fn = ref_pdb_path.stem
        mob_fn = mob_pdb_path.stem

        cmd = [self.binary_path.as_posix(), '-f', self.profit_script_file_path.as_posix()]
        cmd += ['-h', ref_pdb_path.as_posix(), mob_pdb_path.as_posix()]

        logger.info('Launching subprocess "%s"', ' '.join(cmd))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if retcode := process.wait():
            # Logs have a 15k character limit, so log ProFit error line by line.
            logger.error('ProFit failed. ProFit stderr begin:')
            for error_line in stderr.decode('utf-8').splitlines():
                if error_line.strip():
                    logger.error(error_line.strip())
            logger.error('ProFit stderr end')
            logger.error(f"stdout:\n{stdout.decode('latin')}")
            raise RuntimeError(
                f"ProFit failed\nstdout:{stdout.decode('latin')}\nstderr:{stderr.decode('latin')}\n"
            )

        # parse ProFit file or read from stdout
        profit_text = stdout.decode('latin')

        return dict(results=profit_text, ref=ref_fn, 
                    mob=mob_fn, stderr=stderr)

