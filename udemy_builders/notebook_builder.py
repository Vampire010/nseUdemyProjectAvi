import os
import nbformat
import logging
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from helpers import ensure_dir, sanitize_filename, is_texty


class NotebookBuilder:
    def __init__(self, notebooks_dir: str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.notebooks_dir = notebooks_dir

    def _fmt_duration(self, seconds: int) -> str:
        """Convert seconds → mm:ss format."""
        if not seconds or seconds <= 0:
            return "N/A"
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _highlighted_title(self, lec_num: int, lec_title: str) -> str:
        """Format lecture title with highlight style."""
        return f"<div style='background-color:#003366; color:white; padding:8px; border-radius:6px; font-size:18px;'>📘 Lecture {lec_num}: {lec_title}</div>"

    def _duration_block(self, duration: str) -> str:
        return f"<div style='background-color:#e0f7fa; color:#006064; padding:6px; border-radius:6px;'>⏱ Duration: {duration}</div>"

    def _asset_links_block(self, assets) -> str:
        if not assets:
            return "<div style='color:gray;'>No downloadable assets</div>"

        lines = []
        for a in assets:
            title = a.get("asset_title", "asset")
            url = a.get("download_url")
            if url:
                lines.append(f"- [{title}]({url})")
            else:
                lines.append(f"- {title} *(local only)*")
        return "### 📂 Assets\n" + "\n".join(lines)

    def _inline_preview_block(self, asset) -> str:
        """Read texty file and return as Markdown fenced block."""
        path = asset.get("local_path")
        if not path or not os.path.exists(path):
            return ""
        if not is_texty(path):
            return ""

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000)  # preview first ~2000 chars
            fname = os.path.basename(path)
            return f"#### 📄 Preview of *{fname}*:\n```text\n{content}\n```"
        except Exception as e:
            return f"*Could not preview {path}: {e}*"

    def build_notebook(self, course: str, section: str, sec_num: int,
                       lecture: str, lec_num: int, duration_sec: int, lecture_assets: list):
        """Build one notebook per lecture."""
        nb = new_notebook(cells=[])

        # Lecture header
        nb.cells.append(new_markdown_cell(self._highlighted_title(lec_num, lecture)))

        # Duration
        duration_str = self._fmt_duration(duration_sec)
        nb.cells.append(new_markdown_cell(self._duration_block(duration_str)))

        # Assets block
        nb.cells.append(new_markdown_cell(self._asset_links_block(lecture_assets)))

        # Inline previews
        for a in lecture_assets:
            preview = self._inline_preview_block(a)
            if preview:
                nb.cells.append(new_markdown_cell(preview))

        # Save notebook
        save_dir = ensure_dir(os.path.join(
            self.notebooks_dir,
            sanitize_filename(course),
            f"{sec_num:02d}_{sanitize_filename(section)}"
        ))

        nb_path = os.path.join(save_dir, f"{lec_num:02d}_{sanitize_filename(lecture)}.ipynb")
        with open(nb_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        self.log.info("Notebook written → %s", nb_path)
        return nb_path
