from typing import FrozenSet, List
from collections import defaultdict
from itertools import combinations

from game import Tile
from validation import is_valid_group, is_valid_run

def generate_all_possible_melds(tiles: FrozenSet[Tile]) -> List[FrozenSet[Tile]]:
    """Generuje wszystkie możliwe poprawne grupy i szeregi z danego zbioru klocków."""
    possible_melds = set()

    # Optymalizacja: Grupujemy klocki, aby zmniejszyć liczbę kombinacji do sprawdzenia
    tiles_by_number = defaultdict(list)
    tiles_by_color = defaultdict(list)
    for tile in tiles:
        tiles_by_number[tile.number].append(tile)
        tiles_by_color[tile.color].append(tile)

    # 1. Generuj grupy
    for number in tiles_by_number:
        if len(tiles_by_number[number]) >= 3:
            for r in range(3, min(len(tiles_by_number[number]), 4) + 1):
                for group_candidate in combinations(tiles_by_number[number], r):
                    if is_valid_group(list(group_candidate)):
                        possible_melds.add(frozenset(group_candidate))

    # 2. Generuj szeregi
    for color in tiles_by_color:
        if len(tiles_by_color[color]) >= 3:
            sorted_tiles = sorted(list(set(tiles_by_color[color])))
            for r in range(3, len(sorted_tiles) + 1):
                for i in range(len(sorted_tiles) - r + 1):
                    run_candidate = sorted_tiles[i:i + r]
                    if is_valid_run(run_candidate):
                        possible_melds.add(frozenset(run_candidate))

    return list(possible_melds)