import random

from python.tile import Tile
from python.game import GameEngine


# --- Game initialization test ---

def test_initial_state():
    engine = GameEngine(players=2)
    state = engine.state

    assert len(state.hands) == 2
    assert all(len(hand) == 14 for hand in state.hands)
    assert len(state.stock) == len(engine.state.tile_pull) - 14 * 2
    assert state.table == []
    assert state.current_player == 0
    assert not state.done
    assert state.winner is None


# --- Test for enumerate_moves ---

def test_enumerate_moves_basic():
    engine = GameEngine(players=2)
    player = engine.state.current_player
    moves = engine.enumerate_moves(player)

    assert any(used == [] for _, used in moves)  # PASS zawsze obecny
    for new_table, used in moves:
        assert all(tile in engine.state.hands[player] for tile in used)


# --- Test for apply_move and play ---

def test_apply_move_pass_and_play():
    engine = GameEngine(players=2)
    player = engine.state.current_player

    # PASS
    initial_hand_len = len(engine.state.hands[player])
    initial_stock_len = len(engine.state.stock)
    engine.apply_move(player, (engine.state.table, []))
    assert len(engine.state.hands[player]) == initial_hand_len + 1
    assert len(engine.state.stock) == initial_stock_len - 1
    assert engine.state.current_player == 1

    # Zwykły ruch
    engine.state.hands[1] = [Tile(1, "Red"), Tile(2, "Red"), Tile(3, "Red")]
    move = ([ [Tile(1, "Red"), Tile(2, "Red"), Tile(3, "Red")] ], [Tile(1,"Red"), Tile(2,"Red"), Tile(3,"Red")])
    engine.apply_move(1, move)
    assert engine.state.table == [[Tile(1,"Red"), Tile(2,"Red"), Tile(3,"Red")]]
    assert engine.state.hands[1] == []
    assert engine.state.done
    assert engine.state.winner == 1


# --- Test for clone ---

def test_clone_independence():
    engine = GameEngine(players=2)
    clone_state = engine.state.clone()
    assert clone_state.hands == engine.state.hands
    clone_state.hands[0].pop()
    assert len(clone_state.hands[0]) != len(engine.state.hands[0])


# --- Test for full game integration ---

def test_full_game_random_mini():
    engine = GameEngine(players=2, blocks_start=6, blocks_range=5)
    while not engine.state.done:
        player = engine.state.current_player
        moves = engine.enumerate_moves(player)
        move = random.choice(moves)
        engine.apply_move(player, move)
    assert engine.state.done
    assert 0 <= engine.state.winner < engine.state.players
