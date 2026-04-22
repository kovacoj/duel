from pathlib import Path


def test_docs_assets_exist():
    assert Path('docs/index.html').exists(), 'docs/index.html missing'
    assert Path('docs/hero.svg').exists(), 'docs/hero.svg missing'
    assert Path('docs/leaderboard.svg').exists(), 'docs/leaderboard.svg missing'
