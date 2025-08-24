import os
import time
import requests
import logging
from helpers import sanitize_filename, shorten_name, ensure_dir, get_filename_from_url


class AssetDownloader:
    def __init__(self, local_repo=None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.local_repo = os.path.abspath(local_repo) if local_repo else None
        self.sleep = 0.2

    def target_folder(self, downloads_dir, course, section_number, section_title, lecture_title):
        return os.path.join(
            downloads_dir,
            shorten_name(course),
            f"{section_number:02d}_{shorten_name(section_title)}",
            shorten_name(lecture_title)
        )

    def find_local_assets(self, course, section_number, section_title, lecture_title):
        """Look for assets in the local repo, if configured."""
        if not self.local_repo:
            return []

        lecture_dir = os.path.join(
            self.local_repo,
            shorten_name(course),
            f"{section_number:02d}_{shorten_name(section_title)}",
            shorten_name(lecture_title)
        )

        if not os.path.exists(lecture_dir) or not os.path.isdir(lecture_dir):
            return []

        found = []
        try:
            for fname in os.listdir(lecture_dir):
                fpath = os.path.join(lecture_dir, fname)
                if os.path.isfile(fpath):
                    found.append({
                        "asset_title": fname,
                        "local_path": fpath,
                        "download_url": None,
                        "source": "local"
                    })
        except Exception as e:
            self.log.warning("Unable to list assets in %s: %s", lecture_dir, e)
        return found

    def download_assets(self, downloads_dir, course, section_number, section_title, lecture_title, assets):
        """Download remote assets (if not found locally) and merge with local assets."""
        save_dir = ensure_dir(self.target_folder(downloads_dir, course, section_number, section_title, lecture_title))
        merged = self.find_local_assets(course, section_number, section_title, lecture_title)

        for a in (assets or []):
            url = a.get("download_url")
            asset_title = a.get("asset_title") or "asset"

            if not url:
                a["local_path"] = None
                a["source"] = "remote-missing"
                merged.append(a)
                continue

            filename = sanitize_filename(get_filename_from_url(url, asset_title))
            filepath = os.path.join(save_dir, filename)

            if os.path.exists(filepath):
                a["local_path"] = filepath
                a["source"] = "remote-existing"
                merged.append(a)
                continue

            try:
                self.log.info("Downloading %s → %s", asset_title, filepath)
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(filepath, "wb") as f:
                        for chunk in r.iter_content(8192):
                            if chunk:
                                f.write(chunk)
                a["local_path"] = filepath
                a["source"] = "remote-downloaded"
            except Exception as e:
                a["local_path"] = None
                a["download_error"] = str(e)
                a["source"] = "remote-failed"
                self.log.warning("Download failed for %s: %s", filename, e)

            merged.append(a)
            time.sleep(self.sleep)
        return merged
