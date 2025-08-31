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


# --- Tests for generate_all_possible_melds ---

@pytest.mark.parametrize("hand, table, playable, unplayable", [
    # --- przypadek 1: pusta ręka ---
    ([], [], [], []),

    # --- przypadek 2: joker zawsze playable ---
    ([JOKER], [], [JOKER], []),

    # --- przypadek 3: kafel tworzy grupę (1R z 1B i 1Y) ---
    ([Tile(1, R)], [[Tile(1, B), Tile(1, Y)]], [Tile(1, R)], []),

    # --- przypadek 4: kafel tworzy sekwencję (3B z 2B i 4B) ---
    ([Tile(3, B)], [[Tile(2, B), Tile(4, B)]], [Tile(3, B)], []),

    # --- przypadek 5: kafel nieprzydatny (9R bez partnerów) ---
    ([Tile(9, R)], [], [], [Tile(9, R)]),

    # --- przypadek 6: same nieprzydatne
    ([Tile(1, Y), Tile(2, Y), Tile(1, R)],
     [[Tile(9, B), Tile(9, Y), Tile(9, G)]],
     [], [Tile(1, Y), Tile(2, Y), Tile(1, R)]),

    # --- przypadek 7: kilka w ręce, część playable, część nie ---
    ([Tile(5, R), Tile(9, B), JOKER, Tile(1, Y)],
     [[Tile(5, B), Tile(5, Y)], [Tile(8, B), Tile(10, B)]],
     [Tile(5, R), JOKER, Tile(9, B)],   # 5R playable (grupa z 5B, 5Y), JOKER playable
     [Tile(1, Y)]),         # 1B nie tworzy sekwencji/grupy
])
def test_pre_filter_unplayable_tiles(hand, table, playable, unplayable):
    """Tests the pre-filtering of tiles in hand"""
    p, u = pre_filter_unplayable_tiles(hand, table)
    assert sorted(p) == sorted(playable)
    assert sorted(u) == sorted(unplayable)