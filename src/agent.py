from openai import OpenAI
import re


class Agent:
    def __init__(self, config):
        self.config = config['agent']
        
        self.client = OpenAI(
            api_key=self.config.get("api_key"),
            base_url=self.config.get('base_url')
        )

        self.login = {
            "playerName": self.config.get("name"),
            "region": self.config.get("region"),
            "age": self.config.get("age")
        }

    def __call__(self, prompt):
        response = self.client.chat.completions.create(
            model=self.config.get("model"),
            messages=[
                {"role": "system", "content": "You are a quiz player. Select the correct answer from 4 options. Your answer needs to be one of A, B, C, or D. Do not include any explanations or additional text. Only respond with the letter of the correct answer."},
                {"role": "user", "content": prompt}
            ]
        )

        return self.clean_response(
            response.choices[0].message.content
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
    
