import time
import requests
import logging
import json


class UdemyFetcher:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.sleep = 0.3
        self.cookie_headers = {}
        self.cookies = {}

    def load_auth(self, auth_file: str):
        """Load cookies + headers from Authentication.json (exported from browser)."""
        with open(auth_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.cookie_headers = data.get("headers", {})
        self.cookies = data.get("cookies", {})
        self.log.info("Authentication data loaded")

    def fetch_courses(self):
        """Fetch list of subscribed courses."""
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        out = []
        while url:
            r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
            if r.status_code != 200:
                raise RuntimeError(f"Failed to fetch courses: {r.text}")
            data = r.json()
            for c in data.get("results", []):
                out.append({
                    "id": c.get("id"),
                    "title": c.get("title"),
                })
            url = data.get("next")
            time.sleep(self.sleep)
        return out

    def fetch_curriculum_map(self, course_id: int):
        """Fetch section and lecture structure with durations."""
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/public-curriculum-items/?page_size=1000"
        r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        section_map, lecture_map = {}, {}
        if r.status_code == 200:
            current_section_id, current_section_title = None, None
            for item in r.json().get("results", []):
                if item.get("_class") == "chapter":
                    current_section_id = item["id"]
                    current_section_title = item["title"]
                    section_map[current_section_id] = current_section_title
                elif item.get("_class") == "lecture":
                    duration_sec = 0
                    if item.get("asset") and "length" in item["asset"]:
                        duration_sec = item["asset"]["length"]
                    lecture_map[item["id"]] = {
                        "lecture_title": item.get("title"),
                        "section_id": current_section_id,
                        "section_title": current_section_title,
                        "duration_sec": duration_sec,
                    }
        else:
            self.log.error("Failed to fetch curriculum for %s: %s", course_id, r.text)
        return section_map, lecture_map

    def fetch_assets(self, course_id: int, lecture_id: int):
        """Fetch downloadable assets for a lecture."""
        url = f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/supplementary-assets/"
        r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        assets = []
        if r.status_code == 200:
            for a in r.json().get("results", []):
                assets.append({
                    "asset_title": a.get("title"),
                    "download_url": a.get("download_url"),
                })
        else:
            self.log.warning("No assets for lecture %s (course %s): %s", lecture_id, course_id, r.text)
        return assets
