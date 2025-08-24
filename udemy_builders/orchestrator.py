import logging
import os
from helpers import ensure_dir
from downloader import AssetDownloader
from notebook_builder import NotebookBuilder
from fetcher import UdemyFetcher


class UdemyCourseNotebookBuilder:
    def __init__(self, base_folder: str, auth_file: str, local_repo: str = None):
        self.log = logging.getLogger(self.__class__.__name__)

        # Setup folders
        self.downloads_dir = ensure_dir(os.path.join(base_folder, "downloads"))
        self.notebooks_dir = ensure_dir(os.path.join(base_folder, "notebooks"))

        # Init components
        self.fetcher = UdemyFetcher()
        self.fetcher.load_auth(auth_file)
        self.downloader = AssetDownloader(local_repo=local_repo)
        self.nb_builder = NotebookBuilder(self.notebooks_dir)

        self.log.info("Authentication headers initialized")

    def process_course(self, course_id: int, course_title: str):
        self.log.info("Processing course: %s (%s)", course_title, course_id)

        # Fetch structure
        section_map, lecture_map = self.fetcher.fetch_curriculum_map(course_id)
        lecture_count = 0
        notebooks = []

        for lec_id, lec_info in lecture_map.items():
            lecture_count += 1
            lecture_title = lec_info["lecture_title"]
            section_id = lec_info["section_id"]
            section_title = lec_info["section_title"] or "Section"
            duration_sec = lec_info.get("duration_sec", 0)

            # Fetch assets (safe)
            try:
                remote_assets = self.fetcher.fetch_assets(course_id, lec_id)
            except Exception as e:
                self.log.warning("Failed to fetch assets for %s/%s: %s",
                                 course_title, lecture_title, e)
                remote_assets = []

            # Merge with local / download if needed
            downloaded_assets = self.downloader.download_assets(
                downloads_dir=self.downloads_dir,
                course=course_title,
                section_number=len(section_map),  # using len(section_map) → section order
                section_title=section_title,
                lecture_title=lecture_title,
                assets=remote_assets or []
            )

            # Build notebook for this lecture
            nb_path = self.nb_builder.build_notebook(
                course=course_title,
                section=section_title,
                sec_num=list(section_map.keys()).index(section_id) + 1 if section_id else 0,
                lecture=lecture_title,
                lec_num=lecture_count,
                duration_sec=duration_sec,
                lecture_assets=downloaded_assets
            )
            notebooks.append(nb_path)

        return {
            "course": course_title,
            "id": course_id,
            "lectures": lecture_count,
            "notebooks": notebooks
        }

    def run_all_courses(self):
        courses = self.fetcher.fetch_courses()
        results = []
        for c in courses:
            try:
                res = self.process_course(c["id"], c["title"])
                results.append(res)
            except Exception as e:
                self.log.error("Failed course %s (%s): %s", c["title"], c["id"], e)
        self.log.info("Processed %s courses", len(results))
        return results
