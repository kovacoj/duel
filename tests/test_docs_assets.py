from pathlib import Path


def test_docs_assets_exist():
    assert Path('docs/index.html').exists(), 'docs/index.html missing'
    assert Path('docs/hero.svg').exists(), 'docs/hero.svg missing'
    assert Path('docs/leaderboard.svg').exists(), 'docs/leaderboard.svg missing'
    assert Path('docs/summary-chart.svg').exists(), 'docs/summary-chart.svg missing'
    assert Path('docs/site-data.json').exists(), 'docs/site-data.json missing'
