"""One-time (or as-needed) pipeline that enriches a raw dump of posts with
line count, language, and unified tags, ready for few-shot retrieval."""

import json

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from src.config import DEFAULT_PROCESSED_POSTS_PATH, DEFAULT_RAW_POSTS_PATH
from src.llm_client import llm

METADATA_PROMPT = """
You are given a LinkedIn post. Extract the number of lines, the language,
and up to two topic tags.

1. Return valid JSON only. No preamble.
2. The JSON object must have exactly three keys: line_count, language, tags.
3. tags is an array of at most two short text tags.
4. language must be either "English" or "Hinglish" (Hindi + English mix).

Post:
{post}
"""

TAG_UNIFICATION_PROMPT = """
I will give you a list of tags. Unify and merge them into a shorter,
consistent list.

1. Merge near-duplicates, e.g. "Jobseekers" and "Job Hunting" -> "Job Search";
   "Motivation", "Inspiration", "Drive" -> "Motivation";
   "Personal Growth", "Personal Development" -> "Self Improvement";
   "Scam Alert", "Job Scam" -> "Scams".
2. Use title case for every unified tag.
3. Return JSON only, no preamble, mapping each original tag to its unified
   version, e.g. {{"Jobseekers": "Job Search", "Motivation": "Motivation"}}.

Tags:
{tags}
"""


def _run_json_prompt(template: str, **kwargs) -> dict:
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input=kwargs)
    try:
        return JsonOutputParser().parse(response.content)
    except OutputParserException as exc:
        raise OutputParserException(
            "Model response wasn't valid JSON — the input may be too long "
            "or the prompt needs adjusting."
        ) from exc


def extract_metadata(post_text: str) -> dict:
    return _run_json_prompt(METADATA_PROMPT, post=post_text)


def unify_tags(posts_with_metadata: list[dict]) -> dict:
    unique_tags = set()
    for post in posts_with_metadata:
        unique_tags.update(post["tags"])
    return _run_json_prompt(TAG_UNIFICATION_PROMPT, tags=",".join(unique_tags))


def process_posts(
    raw_file_path: str = DEFAULT_RAW_POSTS_PATH,
    processed_file_path: str = DEFAULT_PROCESSED_POSTS_PATH,
) -> None:
    with open(raw_file_path, encoding="utf-8") as f:
        raw_posts = json.load(f)

    enriched_posts = [post | extract_metadata(post["text"]) for post in raw_posts]

    tag_map = unify_tags(enriched_posts)
    for post in enriched_posts:
        post["tags"] = list({tag_map.get(tag, tag) for tag in post["tags"]})

    with open(processed_file_path, encoding="utf-8", mode="w") as f:
        json.dump(enriched_posts, f, indent=4)


if __name__ == "__main__":
    process_posts()
