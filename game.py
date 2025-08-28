from dataclasses import dataclass
from typing import List, Set

# Dataclass dla zwięzłości i czytelności
@dataclass(frozen=True, order=True)
class Tile:
    number: int
    color: str

    def __repr__(self):
        # Ładniejsza reprezentacja do drukowania
        return f"{self.color[0]}{self.number}"

# Definicja Jokera
JOKER = Tile(0, "Joker")


class GameState:
    def __init__(self, hand: Set[Tile], table: List[List[Tile]]):
        self.hand = hand
        self.table = table