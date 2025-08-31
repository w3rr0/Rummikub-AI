import pytest
from tile import Tile
from game import GameEngine


# --- Game initialization test ---

def test_initial_state():
    engine = GameEngine(players=2)
    state = engine.state

    assert len(state.hands) == 2
    assert all(len(hand) == 14 for hand in state.hands)
    assert len(state.stock) == len(GameEngine.TilePull) - 14 * 2
    assert state.table == []
    assert state.current_player == 0
    assert not state.done
    assert state.winner is None