"""Loads previously written posts and serves them up as few-shot examples,
filtered by topic, language, and length bucket."""

import json
from pathlib import Path

import pandas as pd

from src.config import DEFAULT_PROCESSED_POSTS_PATH


class StyleExampleLibrary:
    """In-memory index over a user's past posts, used for few-shot prompting."""

    def __init__(self, file_path: str = DEFAULT_PROCESSED_POSTS_PATH):
        self.posts_df: pd.DataFrame | None = None
        self.available_tags: list[str] = []
        self._load(file_path)

    def _load(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Couldn't find {file_path}. Run the data pipeline "
                "(src/data_pipeline.py) first to generate it from your raw posts."
            )

        with path.open(encoding="utf-8") as f:
            posts = json.load(f)

        self.posts_df = pd.json_normalize(posts)
        self.posts_df["length_bucket"] = self.posts_df["line_count"].apply(self._bucket_length)

        all_tags = self.posts_df["tags"].apply(lambda tags: tags).sum()
        self.available_tags = sorted(set(all_tags))

    @staticmethod
    def _bucket_length(line_count: int) -> str:
        if line_count < 5:
            return "Short"
        if line_count <= 10:
            return "Medium"
        return "Long"

    def find_examples(self, length: str, language: str, tag: str) -> list[dict]:
        """Return past posts matching the requested length/language/topic."""
        df = self.posts_df
        matches = df[
            (df["tags"].apply(lambda tags: tag in tags))
            & (df["language"] == language)
            & (df["length_bucket"] == length)
        ]
        return matches.to_dict(orient="records")

    def get_tags(self) -> list[str]:
        return self.available_tags


if __name__ == "__main__":
    library = StyleExampleLibrary()
    print(library.find_examples("Medium", "Hinglish", "Job Search"))
