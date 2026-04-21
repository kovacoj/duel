from src.duel.parsing import format_prompt, normalize_choice


def test_normalize_choice_handles_common_formats():
    assert normalize_choice("B") == "B"
    assert normalize_choice("answer: c") == "C"
    assert normalize_choice("Možnosť D") == "D"
    assert normalize_choice("I think A is correct") == "A"


def test_format_prompt_normalizes_option_prefixes():
    prompt = format_prompt(
        " Ktoré mesto? ",
        ["A Bratislava", "B) Košice", "C: Nitra", "Žilina"],
    )

    assert prompt == "Ktoré mesto?\nA) Bratislava\nB) Košice\nC) Nitra\nD) Žilina"
