from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def _normalize_ws(s: str) -> str:
    return " ".join((s or "").split())


def _non_dash_text(text: str) -> bool:
    t = (text or "").strip()
    return t not in {"", "-", "–", "—"}


@dataclass(frozen=True)
class QuestionState:
    question: str
    options: list[str]  # raw option texts (may include "A\nParis", etc.)

    def to_prompt(self) -> str:
        lines = [_normalize_ws(self.question)]
        for opt in self.options:
            opt_norm = _normalize_ws(opt)
            # Turn "A Paris" into "A) Paris" when it looks like a letter option
            if len(opt_norm) >= 2 and opt_norm[0] in "ABCD" and opt_norm[1] == " ":
                opt_norm = f"{opt_norm[0]}){opt_norm[1:]}"
            lines.append(opt_norm)
        return "\n".join(lines)


class Client:
    def __init__(self, config: dict, *, headless: bool = True, timeout_s: int = 20):
        self.config = config
        self.game = config.get("game", {})
        self.agent_cfg = config.get("agent", {})

        self.url: str = self.game.get("url", "https://www.duelonline.sk/duelonline_hra.html")

        self.login = {
            "playerName": self.agent_cfg.get("name", ""),
            "age": str(self.agent_cfg.get("age", "") or ""),
            "region": self.agent_cfg.get("region", "") or "",
        }

        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1280,800")

        # Reduce overhead
        chrome_options.page_load_strategy = "eager"
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-networking")

        # Disable images for speed
        chrome_options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
        })

        self.driver = webdriver.Chrome(options=chrome_options)

        # Faster polling than the default 0.5s
        self.wait = WebDriverWait(self.driver, timeout_s, poll_frequency=0.1)

        # Cache current question option buttons (valid only until next render)
        self._last_option_buttons: list = []

    def close(self) -> None:
        self.driver.quit()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        self.driver.get(self.url)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form#start-form")))

    def start_game(self) -> None:
        # Fill form
        name_el = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'form#start-form input[name="playerName"]'))
        )
        age_el = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'form#start-form input[name="age"]'))
        )

        name_el.clear()
        name_el.send_keys(self.login["playerName"])

        age_el.clear()
        age_el.send_keys(self.login["age"])

        if self.login["region"]:
            region_el = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'form#start-form select[name="region"]'))
            )
            Select(region_el).select_by_value(self.login["region"])

        # Click start
        self.wait.until(EC.element_to_be_clickable((By.ID, "start-btn"))).click()

        # Ensure question becomes available
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#screen-quiz")))
        self.wait.until(self._question_ready)

    def read_question(self) -> QuestionState:
        question = (self.driver.find_element(By.ID, "question-text").text or "").strip()
        options = self._read_options()

        # Cache option buttons for immediate clicking (avoids extra waits in answer()).
        self._last_option_buttons = self.driver.find_elements(By.CSS_SELECTOR, "#options button")

        return QuestionState(question=question, options=options)

    def _question_ready(self, d) -> bool:
        t = (d.find_element(By.ID, "question-text").text or "").strip()
        return _non_dash_text(t)

    def _read_options(self) -> list[str]:
        option_selectors = [
            "#options button",
            "#options [role='button']",
            "#options .option",
            "#options .answer",
        ]

        def options_ready(d) -> Optional[list[str]]:
            for css in option_selectors:
                els = d.find_elements(By.CSS_SELECTOR, css)
                texts = [(e.text or "").strip() for e in els]
                texts = [t for t in texts if _non_dash_text(t)]
                if len(texts) >= 2:
                    return texts
            return None

        return self.wait.until(options_ready)

    def _get_question_count(self) -> str:
        try:
            return _normalize_ws(self.driver.find_element(By.ID, "question-count").text)
        except Exception:
            return ""

    def _is_result_active(self) -> bool:
        try:
            el = self.driver.find_element(By.ID, "screen-result")
            cls = (el.get_attribute("class") or "")
            return "active" in cls and el.is_displayed()
        except Exception:
            return False

    def answer(self, choice: str) -> str:
        if choice is None:
            raise ValueError("choice is None")

        letter = choice.strip().upper()[:1]
        if letter not in {"A", "B", "C", "D"}:
            raise ValueError(f"Invalid choice: {choice!r} (expected A/B/C/D)")

        prev_q = _normalize_ws(self.driver.find_element(By.ID, "question-text").text)
        prev_count = self._get_question_count()

        idx = {"A": 0, "B": 1, "C": 2, "D": 3}[letter]

        # Fast path: click cached buttons by DOM order (A,B,C,D)
        clicked = False
        if len(self._last_option_buttons) >= 4:
            try:
                target = self._last_option_buttons[idx]
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                self.driver.execute_script("arguments[0].click();", target)
                clicked = True
            except StaleElementReferenceException:
                clicked = False

        # Slow path: wait for buttons to be populated, then click
        if not clicked:
            def btn_text(btn) -> str:
                return _normalize_ws(btn.get_attribute("textContent") or btn.text or "")

            def options_populated(d):
                btns = d.find_elements(By.CSS_SELECTOR, "#options button")
                if len(btns) < 4:
                    return None
                texts = [btn_text(b) for b in btns]
                if any(t == "" for t in texts):
                    return None
                return btns

            btns = self.wait.until(options_populated)
            target = btns[idx]
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            self.driver.execute_script("arguments[0].click();", target)

        # Wait for next question or result
        def transitioned(d) -> Optional[str]:
            if self._is_result_active():
                return "result"
            q = _normalize_ws(d.find_element(By.ID, "question-text").text)
            c = self._get_question_count()
            if _non_dash_text(q) and (q != prev_q or (c and c != prev_count)):
                return "next"
            return None

        return self.wait.until(transitioned)
    
    def __call__(self, agent):
        self.open()
        self.start_game()

        for idx in range(1, 11):
            question = self.read_question().to_prompt()
            answer = agent(question)
            response = self.answer(answer)

            print(question, answer)

            if response != "next":
                break

        return idx - 1

def main() -> None:
    from .config import config
    from .agent import Agent

    agent = Agent(config)
    client = Client(config, headless=True)

    print(f"score: {client(agent)}")

if __name__ == "__main__":
    main()
