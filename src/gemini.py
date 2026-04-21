from google import genai
from google.genai import types
import re


class Agent:
    def __init__(self, config):
        self.config = config.get('gemini', {})

        self.client = genai.Client(
            api_key=self.config.get("api_key")
        )

    def __call__(self, prompt):
        response = self.client.models.generate_content(
            model=self.config.get("model", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                # thinking_config=types.ThinkingConfig(thinking_level="low"),
                system_instruction="You are a quiz player. Select the correct answer from 4 options. Your answer needs to be one of A, B, C, or D. Do not include any explanations or additional text. Only respond with the letter of the correct answer."
            )
        )

        return self.clean_response(
            response.text
        )
    
    def clean_response(self, response):
        patterns = [
            r"^\(?\s*([ABCD])\s*\)?\s*[\)\.\:\-]?\s*$",
            r"^\(?\s*([ABCD])\s*\)?\s*[\)\.\:\-]\s+",
            r"(?i)\banswer\s*[:\-]?\s*\(?\s*([ABCD])\s*\)?\b",
        ]

        text = response.strip()
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                return m.group(1).upper()

        m = re.search(r"\b([ABCD])\b", text, flags=re.IGNORECASE)

        return m.group(1).upper() if m else None


if __name__ == "__main__":
    from .config import config

    agent = Agent(config)
    prompt = """
                Ktoré ovocie sa po česky povie švestky?
                    A) marhule
                    B) hrušky
                    C) slivky
                    D) čerešne C
            """

    response = agent(prompt)

    print(response)
    
