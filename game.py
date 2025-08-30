from dataclasses import dataclass
from typing import List, Literal, Optional
import random

TileColor = Literal['Red', 'Blue', 'Yellow', 'Black', 'Joker']

# Dataclass dla zwięzłości i czytelności
@dataclass(frozen=True, order=True)
class Tile:
    number: int
    color: TileColor

    def __repr__(self):
        # Ładniejsza reprezentacja do drukowania
        return f"{self.color[0]}{self.number}"


class GameState:
    def __init__(self, players: int):
        # Draw pile
        self.stock = GameEngine.TilePull.copy()
        random.shuffle(self.stock)

        # Deal tiles
        self.hands = [[self.stock.pop() for _ in range(14)] for _ in range(players)]

        # Init table
        self.table: List[List[Tile]] = []

        self.players = players
        self.current_player = 0
        self.done = False
        self.winner = Optional[int] = None

    def clone(self):
        st = GameState(self.players)
        st.stock = self.stock.copy()
        st.hands = [hand.copy() for hand in self.hands]
        st.table = [meld.copy() for meld in self.table]
        st.current_player = self.current_player
        st.done = self.done
        st.winner = self.winner
        return st


class GameEngine:
    TilePull = ([Tile(number, color)
                for color in ['Red', 'Blue', 'Yellow', 'Black']
                for number in range(1, 14)]
                + [Tile(0, 'Joker')]) * 2

    def __init__(self, players: int = 2):
        self.state = GameState(players)

