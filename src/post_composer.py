"""Builds prompts and generates new posts styled after a user's past writing."""

from src.config import LENGTH_TO_LINE_RANGE, MAX_STYLE_EXAMPLES
from src.llm_client import llm
from src.style_examples import StyleExampleLibrary


class PostComposer:
    """Generates a new post in a given topic/length/language, few-shot styled
    from the user's own historical posts."""

    def __init__(self, style_library: StyleExampleLibrary | None = None):
        self.style_library = style_library or StyleExampleLibrary()

    def generate(self, length: str, language: str, tag: str) -> str:
        prompt = self._build_prompt(length, language, tag)
        response = llm.invoke(prompt)
        return response.content

    def _build_prompt(self, length: str, language: str, tag: str) -> str:
        line_range = LENGTH_TO_LINE_RANGE[length]

        prompt = f"""
        Generate a LinkedIn post using the information below. No preamble.

        1) Topic: {tag}
        2) Length: {line_range}
        3) Language: {language}
        If the language is Hinglish, mix Hindi and English, but write the
        post using English script throughout.
        """

        examples = self.style_library.find_examples(length, language, tag)
        if examples:
            prompt += "4) Match the writing style shown in the examples below."

        for i, example in enumerate(examples[:MAX_STYLE_EXAMPLES]):
            prompt += f"\n\nExample {i + 1}:\n\n{example['text']}"

        return prompt


if __name__ == "__main__":
    composer = PostComposer()
    print(composer.generate("Medium", "English", "Mental Health"))
