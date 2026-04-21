from __future__ import annotations

import re
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .models import Question
from .parsing import normalize_ws


def _non_dash_text(text: str) -> bool:
    return (text or "").strip() not in {"", "-", "–", "—"}


@dataclass(frozen=True)
class ResultState:
    title: str
    meta: str
    summary: str
    message: str
    time_text: str
    score: int | None
    max_score: int | None


class LiveGameClient:
    def __init__(self, config: dict, *, headless: bool = True, timeout_s: int = 20):
        self.config = config
        self.url = config.get("game", {}).get("url", "https://www.duelonline.sk/duelonline_hra.html")
        player = config.get("player", {})
        self.player = {
            "name": player.get("name", ""),
            "age": str(player.get("age", "") or ""),
            "region": player.get("region", "") or "",
        }

        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1280,800")
        chrome_options.page_load_strategy = "eager"
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_experimental_option(
            "prefs",
            {"profile.managed_default_content_settings.images": 2},
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, timeout_s, poll_frequency=0.1)
        self._last_option_buttons: list = []

    def close(self) -> None:
        self.driver.quit()

    def __enter__(self) -> "LiveGameClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        self.driver.get(self.url)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form#start-form")))

    def start_game(self) -> None:
        name_el = self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'form#start-form input[name="playerName"]')
            )
        )
        age_el = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'form#start-form input[name="age"]'))
        )

        name_el.clear()
        name_el.send_keys(self.player["name"])
        age_el.clear()
        age_el.send_keys(self.player["age"])

        if self.player["region"]:
            region_el = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'form#start-form select[name="region"]')
                )
            )
            Select(region_el).select_by_value(self.player["region"])

        self.wait.until(EC.element_to_be_clickable((By.ID, "start-btn"))).click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#screen-quiz")))
        self.wait.until(self._question_ready)

    def read_question(self, index: int) -> Question:
        question = (self.driver.find_element(By.ID, "question-text").text or "").strip()
        options = self._read_options()
        self._last_option_buttons = self.driver.find_elements(By.CSS_SELECTOR, "#options button")
        return Question(index=index, question=question, options=options)

    def answer(self, choice: str) -> str:
        if choice is None:
            raise ValueError("choice is None")

        letter = choice.strip().upper()[:1]
        if letter not in {"A", "B", "C", "D"}:
            raise ValueError(f"Invalid choice: {choice!r} (expected A/B/C/D)")

        prev_q = normalize_ws(self.driver.find_element(By.ID, "question-text").text)
        prev_count = self._get_question_count()
        idx = {"A": 0, "B": 1, "C": 2, "D": 3}[letter]

        clicked = False
        if len(self._last_option_buttons) >= 4:
            try:
                target = self._last_option_buttons[idx]
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
                self.driver.execute_script("arguments[0].click();", target)
                clicked = True
            except StaleElementReferenceException:
                clicked = False

        if not clicked:
            def populated(d):
                buttons = d.find_elements(By.CSS_SELECTOR, "#options button")
                if len(buttons) < 4:
                    return None
                texts = [
                    normalize_ws(button.get_attribute("textContent") or button.text or "")
                    for button in buttons
                ]
                return buttons if all(texts) else None

            buttons = self.wait.until(populated)
            target = buttons[idx]
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            self.driver.execute_script("arguments[0].click();", target)

        def transitioned(d):
            if self._is_result_active():
                return "result"
            question_text = normalize_ws(d.find_element(By.ID, "question-text").text)
            question_count = self._get_question_count()
            if _non_dash_text(question_text) and (
                question_text != prev_q or (question_count and question_count != prev_count)
            ):
                return "next"
            return None

        return self.wait.until(transitioned)

    def read_result(self) -> ResultState:
        self.wait.until(lambda d: self._is_result_active())
        fields = {
            "title": self._read_text(By.ID, "result-title"),
            "meta": self._read_text(By.ID, "result-meta"),
            "summary": self._read_text(By.ID, "result-summary"),
            "message": self._read_text(By.ID, "result-message"),
            "time_text": self._read_text(By.ID, "result-time"),
        }
        score, max_score = self._parse_score(fields)
        return ResultState(score=score, max_score=max_score, **fields)

    def _read_text(self, by: str, value: str) -> str:
        try:
            return normalize_ws(self.driver.find_element(by, value).text)
        except Exception:
            return ""

    def _question_ready(self, driver) -> bool:
        return _non_dash_text((driver.find_element(By.ID, "question-text").text or "").strip())

    def _read_options(self) -> list[str]:
        option_selectors = [
            "#options button",
            "#options [role='button']",
            "#options .option",
            "#options .answer",
        ]

        def options_ready(driver):
            for css in option_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, css)
                texts = [(element.text or "").strip() for element in elements]
                texts = [text for text in texts if _non_dash_text(text)]
                if len(texts) >= 2:
                    return texts
            return None

        return self.wait.until(options_ready)

    def _get_question_count(self) -> str:
        try:
            return normalize_ws(self.driver.find_element(By.ID, "question-count").text)
        except Exception:
            return ""

    def _is_result_active(self) -> bool:
        try:
            element = self.driver.find_element(By.ID, "screen-result")
            classes = element.get_attribute("class") or ""
            return "active" in classes and element.is_displayed()
        except Exception:
            return False

    def _parse_score(self, fields: dict[str, str]) -> tuple[int | None, int | None]:
        haystack = " | ".join(fields.values())
        for pattern in (r"(\d+)\s*/\s*(\d+)", r"(\d+)\s*z\s*(\d+)"):
            match = re.search(pattern, haystack, flags=re.IGNORECASE)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None, None
