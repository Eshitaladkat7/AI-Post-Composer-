"""Central place for constants used across the app.

Keeping these in one spot instead of scattered across files makes it easy
to add a new length bucket or language option without touching UI or
prompt-building logic.
"""

LENGTH_TO_LINE_RANGE = {
    "Short": "1 to 5 lines",
    "Medium": "6 to 10 lines",
    "Long": "11 to 15 lines",
}

LENGTH_OPTIONS = list(LENGTH_TO_LINE_RANGE.keys())
LANGUAGE_OPTIONS = ["English", "Hinglish"]

MAX_STYLE_EXAMPLES = 2  # how many past posts to feed the model as style reference

DEFAULT_PROCESSED_POSTS_PATH = "data/processed_posts.json"
DEFAULT_RAW_POSTS_PATH = "data/raw_posts.json"

GROQ_MODEL_NAME = "openai/gpt-oss-120b"
