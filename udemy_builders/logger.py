import logging
import os
from datetime import datetime

def setup_logging(base_folder: str):
    logs_dir = os.path.join(base_folder, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    logfile = os.path.join(logs_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Root logger
    logging.basicConfig(level=logging.INFO, format=fmt, datefmt=datefmt)

    # File handler (detailed)
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(fmt, datefmt))

    # Console handler (info+)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(fmt, datefmt))

    root = logging.getLogger()
    root.addHandler(fh)
    root.addHandler(ch)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging initialized → %s", logfile)
    return logfile
