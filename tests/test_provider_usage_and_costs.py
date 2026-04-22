from src.duel.costs import estimate_cost
from src.duel.providers.gemini_provider import GeminiProvider
from src.duel.runner import run_replay


class DummyProvider:
    name = "dummy"
    model = "gemini-2.5-flash"

    def answer(self, question):
        from src.duel.models import ProviderResponse

        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response=question.correct_choice or "A",
            answer=question.correct_choice or "A",
            latency_ms=5,
            usage={
                "prompt_tokens": 10,
                "response_tokens": 2,
                "total_tokens": 12,
            },
        )


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
    assert calls["http_options"] and calls["http_options"].get("base_url") == "https://custom.local/"


def test_run_replay_aggregates_token_usage_and_cost():
    artifact = run_replay(DummyProvider(), "examples/replay_sample.json")

    assert artifact.token_usage == {
        "prompt_tokens": 50,
        "response_tokens": 10,
        "total_tokens": 60,
    }
    assert artifact.estimated_cost_usd is not None
