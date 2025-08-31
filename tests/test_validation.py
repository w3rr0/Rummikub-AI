import pytest
from tile import Tile
from validation import is_valid_group, is_valid_meld, is_table_valid, is_valid_run

# Definicje kolorów dla czytelności testów
R = "Red"
B = "Blue"
G = "Black"
Y = "Yellow"

# Definicja JOKERA
JOKER = Tile(0, "Joker")

# --- Testy dla is_valid_group ---

@pytest.mark.parametrize("group, expected", [
    # Poprawne grupy
    ([Tile(7, R), Tile(7, B), Tile(7, G)], True),
    ([Tile(1, R), Tile(1, B), Tile(1, G), Tile(1, Y)], True),
    ([Tile(5, R), Tile(5, B), JOKER], True),
    ([Tile(10, R), Tile(10, B), Tile(10, G), JOKER], True),
    ([Tile(12, Y), Tile(12, B), JOKER, JOKER], True),

    # Niepoprawne grupy
    ([Tile(7, R), Tile(7, B)], False),  # Za krótka
    ([Tile(1, R), Tile(1, B), Tile(1, G), Tile(1, Y), Tile(1, R)], False), # Za długa
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


# --- Testy dla is_table_valid ---

@pytest.mark.parametrize("table, expected", [
    # Poprawne stoły
    ([], True), # Pusty stół jest poprawny
    (
        [
            [Tile(7, R), Tile(7, B), Tile(7, G)],
            [Tile(1, Y), Tile(2, Y), Tile(3, Y), Tile(4, Y)]
        ],
        True
    ),
    (
        [
            [Tile(10, R), JOKER, Tile(10, B)],
            [Tile(5, G), Tile(6, G), JOKER]
        ],
        True
    ),

    # Niepoprawne stoły
    (
        [
            [Tile(7, R), Tile(7, B)] # Jeden z układów jest niepoprawny
        ],
        False
    ),
    (
        [
            [Tile(7, R), Tile(7, B), Tile(7, G)], # Poprawny
            [Tile(1, Y), Tile(3, Y), Tile(4, Y)]  # Niepoprawny
        ],
        False
    ),
])
def test_is_table_valid(table, expected):
    """Testuje walidację całego stołu."""
    assert is_table_valid(table) == expected

def test_is_valid_run_with_fix():
    """
    Ten test sprawdza konkretnie przypadek, który byłby błędny
    bez sugerowanej poprawki w validation.py.
    """
    # Ten szereg jest niepoprawny, ponieważ zawiera dwa razy klocek "Czerwony 7"
    invalid_run_with_duplicates = [Tile(7, R), Tile(7, R), Tile(8, R)]
    assert not is_valid_run(invalid_run_with_duplicates)
