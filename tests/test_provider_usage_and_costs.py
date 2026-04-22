from src.duel.providers.gemini_provider import GeminiProvider
from src.duel.providers.openai_provider import OpenAIProvider
from src.duel.costs import estimate_cost


def test_estimate_cost_default_rate():
    usage = {"prompt_tokens": 100, "response_tokens": 50, "total_tokens": 150}
    cost = estimate_cost(usage, "gemini-2.5-flash")
    assert cost is not None and cost >= 0


def test_gemini_base_url_passed_to_client(monkeypatch, tmp_path):
    # monkeypatch genai.Client to capture http_options
    calls = {}

    class DummyClient:
        def __init__(self, api_key=None, http_options=None):
            calls['api_key'] = api_key
            calls['http_options'] = http_options

    monkeypatch.setattr('google.genai.Client', DummyClient)
    settings = {"api_key": "x", "base_url": "https://custom.local/"}
    GeminiProvider(settings)
    assert calls['http_options'] and calls['http_options'].get('base_url') == "https://custom.local/"
