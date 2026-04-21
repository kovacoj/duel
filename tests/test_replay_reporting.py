
from src.duel.browser import ResultState
from src.duel.providers.offline import BaselineProvider, OracleProvider
from src.duel.reporting import load_artifacts, write_report
from src.duel.runner import _infer_live_correctness, run_replay
from src.duel.storage import save_run_artifact


def test_replay_runner_scores_oracle_dataset():
    artifact = run_replay(OracleProvider(), "examples/replay_sample.json")

    assert artifact.score == 5
    assert artifact.max_score == 5
    assert artifact.status == "completed"
    assert len(artifact.questions) == 5


def test_report_generation_aggregates_saved_runs(tmp_path):
    runs_dir = tmp_path / "runs"
    oracle_artifact = run_replay(OracleProvider(), "examples/replay_sample.json")
    baseline_artifact = run_replay(BaselineProvider(), "examples/replay_sample.json")

    save_run_artifact(oracle_artifact, runs_dir)
    save_run_artifact(baseline_artifact, runs_dir)

    markdown_path, summary_path = write_report(
        runs_dir,
        tmp_path / "leaderboard.md",
        tmp_path / "summary.json",
    )

    artifacts = load_artifacts(runs_dir)
    summary = summary_path.read_text(encoding="utf-8")
    markdown = markdown_path.read_text(encoding="utf-8")

    assert len(artifacts) == 2
    assert '"run_count": 2' in summary
    assert "oracle" in markdown
    assert "baseline" in markdown


def test_replay_runner_uses_live_transition_labels():
    artifact = run_replay(OracleProvider(), "examples/replay_sample.json")

    assert [question.transition for question in artifact.questions] == ["next"] * 5


def test_infer_live_correctness_false_when_result_score_does_not_increase():
    result_state = ResultState(
        title="Koniec hry",
        meta="",
        summary="",
        message="",
        time_text="",
        score=0,
        max_score=10,
    )

    assert _infer_live_correctness(0, result_state, "result") is False
