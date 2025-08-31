import pytest
from tile import Tile
from generation import generate_all_possible_melds, pre_filter_unplayable_tiles, find_all_valid_moves, possible_moves

# Definicje kolorów dla czytelności testów
R = "Red"
B = "Blue"
G = "Black"
Y = "Yellow"

# Definicja JOKERA
JOKER = Tile(0, "Joker")

# --- Tests for generate_all_possible_melds ---

@pytest.mark.parametrize("group, expected", [
    # Simple run
    ([Tile(1, B), Tile(2, B), Tile(3, B)],
     [(Tile(1, B), Tile(2, B), Tile(3, B))]),

    # Simple group
    ([Tile(1, B), Tile(1, G), Tile(1, R)],
     [(Tile(1, B), Tile(1, G), Tile(1, R))]),

    # Group and run
    ([Tile(1, B), Tile(2, B), Tile(3, B), Tile(1, G), Tile(2, G), Tile(3, G), Tile(1, Y), Tile(2, Y), Tile(3, Y)],
     [
         (Tile(1, B), Tile(2, B), Tile(3, B)), (Tile(1, G), Tile(2, G), Tile(3, G)), (Tile(1, Y), Tile(2, Y), Tile(3, Y)),
         (Tile(1, B), Tile(1, G), Tile(1, Y)), (Tile(2, B), Tile(2, G), Tile(2, Y)), (Tile(3, B), Tile(3, G), Tile(3, Y))
     ]),
])
def test_generate_all_possible_melds(group, expected):
    """Tests the generation of correct melds"""
    assert {frozenset(meld) for meld in generate_all_possible_melds(group)} == {frozenset(meld) for meld in expected}
