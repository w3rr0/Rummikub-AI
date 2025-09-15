from typing import List, Optional, Tuple
import random

from generation import possible_moves as ps
from tile import Tile


class GameState:
    def __init__(self, players: int, blocks: int = 14, r: int = 13):
        self.tile_pull = ([Tile(number, color)
                           for color in ['Red', 'Blue', 'Yellow', 'Black']
                           for number in range(1, r+1)]
                          ) * 2 + [Tile(1, 'Joker'), Tile(1, 'Joker')]

        # Draw pile
        self.stock = self.tile_pull.copy()
        random.shuffle(self.stock)

        # Deal tiles
        self.hands = [[self.stock.pop() for _ in range(blocks)] for _ in range(players)]

        # Init table
        self.table: List[List[Tile]] = []

        self.player_putted = False
        self.players = players
        self.current_player = 0
        self.done = False
        self.winner: Optional[int] = None

    def clone(self):
        st = GameState(self.players)
        st.stock = self.stock.copy()
        st.hands = [hand.copy() for hand in self.hands]
        st.table = [meld.copy() for meld in self.table]
        st.current_player = self.current_player
        st.done = self.done
        st.winner = self.winner
        st.player_putted = self.player_putted
        return st


class GameEngine:
    def __init__(self, players: int = 2, blocks_start: int = 14, blocks_range: int = 13):
        self.state = GameState(players, blocks_start, blocks_range)
        self.tile_pull = ([Tile(number, color)
                     for color in ['Red', 'Blue', 'Yellow', 'Black']
                     for number in range(1, 14)]
                    + [Tile(1, 'Joker')]) * 2

    def enumerate_moves(self, player: int):
        hand = self.state.hands[player]
        table = self.state.table

        moves = ps(hand, table, 3)

        return moves

    def apply_move(self, player: int, move: Tuple[List[List[Tile]], List[Tile]]) -> None:
        new_table, used_tiles = move

        # Draw a card
        if len(used_tiles) == 0:
            raise ValueError("Incorrect move")
        else:
            for tile in used_tiles:
                if tile not in self.state.hands[player]:
                    raise ValueError(f"Player does not have the required tile: {tile}")
                self.state.hands[player].remove(tile)

            self.state.table = [meld.copy() for meld in new_table]

            if len(self.state.hands[player]) == 0:
                self.state.done = True
                self.state.winner = player


    def next_player(self, placed: bool) -> None:
        player = self.state.current_player
        if not placed:
            # Draw a tile
            if not self.state.stock:
                raise ValueError("Draws from an empty stock")
            else:
                self.state.hands[player].append(self.state.stock.pop())

        self.state.player_putted = False

        # Player change
        self.state.current_player = (self.state.current_player + 1) % self.state.players