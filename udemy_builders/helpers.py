import os
import re
import logging
import time


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    """Keep letters, numbers, spaces, and underscores. Replace others with underscore."""
    return re.sub(r"[^A-Za-z0-9 _-]", "_", name)


def shorten_name(name: str, max_len: int = 100) -> str:
    clean = sanitize_filename(name)
    return clean[:max_len]


def get_filename_from_url(url: str, fallback: str = "asset") -> str:
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename or fallback


def is_texty(path: str) -> bool:
    """Decide if a file is 'text-like' (good candidate for inline preview)."""
    text_exts = [".txt", ".md", ".csv", ".json", ".xml", ".py", ".sql", ".log", ".ini"]
    return any(path.lower().endswith(ext) for ext in text_exts)


def init_logger(base_folder: str):
    logs_dir = ensure_dir(os.path.join(base_folder, "logs"))
    logfile = os.path.join(
        logs_dir,
        f"pipeline_{time.strftime('%Y%m%d_%H%M%S')}.log"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(logfile, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging initialized → %s", logfile)
    return logfile
