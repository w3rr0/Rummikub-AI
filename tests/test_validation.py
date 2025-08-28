import pytest
from game import Tile, JOKER
from validation import is_valid_group, is_valid_meld

# Definicje kolorów dla czytelności testów
R = "Red"
B = "Blue"
G = "Green"
O = "Orange"

# --- Testy dla is_valid_group ---

@pytest.mark.parametrize("group, expected", [
    # Poprawne grupy
    ([Tile(7, R), Tile(7, B), Tile(7, G)], True),
    ([Tile(1, R), Tile(1, B), Tile(1, G), Tile(1, O)], True),
    ([Tile(5, R), Tile(5, B), JOKER], True),
    ([Tile(10, R), Tile(10, B), Tile(10, G), JOKER], True),
    ([Tile(12, O), Tile(12, B), JOKER, JOKER], True),

    # Niepoprawne grupy
    ([Tile(7, R), Tile(7, B)], False),  # Za krótka
    ([Tile(1, R), Tile(1, B), Tile(1, G), Tile(1, O), Tile(1, R)], False), # Za długa
    ([Tile(7, R), Tile(8, R), Tile(9, R)], False), # To szereg, nie grupa
    ([Tile(7, R), Tile(7, B), Tile(8, G)], False), # Różne numery
    ([Tile(7, R), Tile(7, R), Tile(7, B)], False), # Zduplikowany kolor
    ([Tile(7, R), Tile(7, R), JOKER], False), # Zduplikowany kolor z jokerem
    ([], False), # Pusta lista
])
def test_is_valid_group(group, expected):
    """Testuje walidację grup."""
    assert is_valid_group(group) == expected


# --- Testy dla is_valid_meld ---

@pytest.mark.parametrize("meld, expected", [
    # Poprawna grupa
    ([Tile(5, R), Tile(5, B), Tile(5, G)], True),
    # Poprawny szereg
    ([Tile(5, R), Tile(6, R), Tile(7, R)], True),
    # Niepoprawny układ
    ([Tile(5, R), Tile(6, B), Tile(7, G)], False),
    ([Tile(1, R), Tile(1, R)], False),
])
def test_is_valid_meld(meld, expected):
    """Testuje, czy układ jest poprawną grupą LUB szeregiem."""
    assert is_valid_meld(meld) == expected
