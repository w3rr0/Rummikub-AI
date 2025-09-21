import pytest
from python.tile import Tile
from python.generation import generate_all_possible_melds, pre_filter_unplayable_tiles, find_all_valid_moves, possible_moves

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


# --- Tests for find_all_valid_moves ---

@pytest.mark.parametrize("hand, table, first_only, expected_count", [
    # --- przypadek 1: pusty stan ---
    ([], [], False, 0),

    # --- przypadek 2: prosty run 1 ---
    ([Tile(1, B)], [[Tile(2, B), Tile(3, B)]], False, 1),

    # --- przypadek 3: prosty group 1 ---
    ([Tile(1, R)], [[Tile(1, B), Tile(1, Y)]], False, 1),

    # --- przypadek 4: Nie ma żadnej możliwości ---
    ([Tile(1, R), Tile(2, R)], [[Tile(2, B), Tile(3, B)]], False, 0),

    # --- przypadek 5: first_only=True ---
    ([Tile(1, R), Tile(2, R)], [[JOKER, Tile(3, R)]], True, 1),

    # --- przypadek 6: Joker użyty w run ---
    ([JOKER], [[Tile(2, B), Tile(3, B)]], False, 1),
])
def test_find_all_valid_moves(hand, table, first_only, expected_count):
    """Tests finding all possible solutions for a given hand and table"""
    moves = find_all_valid_moves(hand, table, first_only)
    assert isinstance(moves, list)
    assert all(isinstance(layout, list) and all(isinstance(m, list) for m in layout) for layout in moves)
    assert len(moves) == expected_count

    # All moves must use tiles from hand
    for move in moves:
        used_from_hand = sum((tile in hand) for meld in move for tile in meld)
        assert used_from_hand > 0 or (hand == [] and table == [])


# --- Tests for possible_moves ---

@pytest.mark.parametrize("hand, table, expected_count", [
    # --- przypadek 1: pusty stan ---
    ([], [], 0),

    # --- przypadek 2: Joker w ręce ---
    ([JOKER], [[Tile(2, B), Tile(3, B)]], 1),

    # --- przypadek 3: prosty run 1 ---
    ([Tile(1, B)], [[Tile(2, B), Tile(3, B)]], 1),

    # --- przypadek 4: prosty group 1 ---
    ([Tile(1, R)], [[Tile(1, B), Tile(1, Y)]], 1),

    # --- przypadek 5: kilka możliwości dla kilku kafli ---
    ([Tile(1, R), Tile(2, R)], [[JOKER, Tile(3, R)]], 3),
])
def test_possible_moves(hand, table, expected_count):
    moves = possible_moves(hand, table)
    assert isinstance(moves, list)
    assert len(moves) == expected_count

    for new_table, used_tiles in moves:
        # nowa tabela jest listą list kafli
        assert all(isinstance(meld, list) for meld in new_table)
        assert all(all(isinstance(t, Tile) for t in meld) for meld in new_table)
        # użyte kafle pochodzą z ręki
        assert all(tile in hand for tile in used_tiles)
        # nie zwracamy pustego ruchu
        assert len(used_tiles) > 0
        # table_signature unikalne
        table_signature = frozenset(frozenset(meld) for meld in new_table)
        assert table_signature == frozenset(frozenset(meld) for meld in new_table)