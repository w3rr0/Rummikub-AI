from typing import List
from tile import Tile


def is_valid_group(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawną GRUPĄ."""
    if len(tiles) < 3 or len(tiles) > 4:
        return False

    non_jokers = [tile for tile in tiles if tile.color != 'Joker']

    # Jeśli są klocki inne niż jokery, sprawdź ich numery
    if non_jokers:
        first_number = non_jokers[0].number
        if not all(tile.number == first_number for tile in non_jokers):
            return False

    # Sprawdź unikalność kolorów
    colors = {tile.color for tile in non_jokers}
    if len(colors) != len(non_jokers):
        return False

    return True


def is_valid_run(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawnym SZEREGIEM (nowa, poprawiona wersja)."""
    if len(tiles) < 3:
        return False

    non_jokers = sorted([tile for tile in tiles if tile.color != 'Joker'])

    if not non_jokers:
        return True

    main_color = non_jokers[0].color
    if not all(tile.color == main_color for tile in non_jokers):
        return False

    numbers = [tile.number for tile in non_jokers]
    if len(numbers) != len(set(numbers)):
        return False

    min_num = numbers[0]
    max_num = numbers[-1]

    span = max_num - min_num + 1

    if span > len(tiles):
        return False

    return True

def is_valid_meld(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawną grupą LUB szeregiem."""
    return is_valid_group(tiles) or is_valid_run(tiles)

def is_table_valid(table: List[List[Tile]]) -> bool:
    """Sprawdza, czy cały stół jest poprawny."""
    if not table:
        return True
    return all(is_valid_meld(meld) for meld in table)
