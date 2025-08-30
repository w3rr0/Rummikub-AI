from dataclasses import dataclass
from typing import List, Literal

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
    def __init__(self, hand: List[Tile], table: List[List[Tile]]):
        self.hand = hand
        self.table = table