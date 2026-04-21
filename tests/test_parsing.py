from src.duel.parsing import choice_to_index, format_prompt, normalize_choice


def test_normalize_choice_handles_common_formats():
    assert normalize_choice("B") == "B"
    assert normalize_choice("answer: c") == "C"
    assert normalize_choice("Možnosť D") == "D"
    assert normalize_choice("I think A is correct") == "A"


def test_normalize_choice_rejects_empty_or_non_choice_text():
    assert normalize_choice(None) is None
    assert normalize_choice("") is None
    assert normalize_choice("Aloha") is None


def test_choice_to_index_maps_normalized_choice():
    assert choice_to_index("c") == 2
    assert choice_to_index("invalid") is None


def test_format_prompt_normalizes_option_prefixes():
    prompt = format_prompt(
        " Ktoré mesto? ",
        ["A Bratislava", "B) Košice", "C: Nitra", "Žilina"],
    )

    assert prompt == "Ktoré mesto?\nA) Bratislava\nB) Košice\nC) Nitra\nD) Žilina"
