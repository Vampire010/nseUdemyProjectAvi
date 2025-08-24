# run.py
import os
from helpers import init_logger
from orchestrator import UdemyCourseNotebookBuilder

BASE = os.path.join(os.path.dirname(__file__), "udemyDownloads")
AUTH_FILE = os.path.join(os.path.dirname(__file__), "Authentication.json")
LOCAL_REPO = os.path.join(BASE, "downloads")  # optional, can be None

if __name__ == "__main__":
    logfile = init_logger(BASE)
    print("Logs →", logfile)

    builder = UdemyCourseNotebookBuilder(
        base_folder=BASE,
        auth_file=AUTH_FILE,
        local_repo=LOCAL_REPO
    )

    summary = builder.run_all_courses()
    print(summary)
