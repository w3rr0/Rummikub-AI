from typing import List
from game import Tile, JOKER

def is_valid_group(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawną GRUPĄ."""
    if len(tiles) < 3 or len(tiles) > 4:
        return False

    numbers = {tile.number for tile in tiles if tile != JOKER}
    if len(numbers) > 1:  # Wszystkie muszą mieć ten sam numer
        return False

    colors = {tile.color for tile in tiles if tile != JOKER}
    if len(colors) != len([t for t in tiles if t != JOKER]):  # Sprawdzenie unikalności kolorów
        return False

    return True