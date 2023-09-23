import logging
import os
import sys
import time


def setup_logger(save_dir=None, info_file_name="run.log", err_file_name="run.err",
                 distributed_rank=0, level=logging.INFO, time_stamp: bool = True):
    def _formatter_factory(level):
        # define format according to logging level
        fmt = '%(asctime)s [%(threadName)s] [%(levelname)s] %(name)s - %(message)s'
        if level in [logging.DEBUG, logging.ERROR]:
            fmt = '%(asctime)s {%(pathname)s:%(lineno)d} [%(levelname)s] %(name)s - %(message)s [%(threadName)s]'
        formatter = logging.Formatter(
            fmt=fmt,
            datefmt='%H:%M:%S')

        return formatter

    time_tag = ""
    if time_stamp:
        time_tag = time.strftime("%Y%B%d.%H%M%S")
        fn = os.path.splitext(info_file_name)[0]
        info_file_name = f"{fn}-{time_tag}.log"
        err_file_name = f"{fn}-{time_tag}.err"

    logger = logging.getLogger()
    logger.setLevel(level)
    # don't log results for the non-master process
    if distributed_rank > 0:
        return logger
    # 1. output to sys.stdout
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(_formatter_factory(level))
    logger.addHandler(ch)

    # 2. output to log file
    if save_dir:
        # info
        fh = logging.FileHandler(os.path.join(save_dir, info_file_name), mode='w')
        fh.setLevel(level)
        fh.setFormatter(_formatter_factory(level))
        logger.addHandler(fh)
        # error
        fh_err = logging.FileHandler(os.path.join(save_dir, err_file_name), mode='w')
        fh_err.setLevel(logging.ERROR)
        fh_err.setFormatter(_formatter_factory(logging.ERROR))
        logger.addHandler(fh_err)

    return logger
