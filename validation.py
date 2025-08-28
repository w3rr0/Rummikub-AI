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


def is_valid_run(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawnym SZEREGIEM."""
    if len(tiles) < 3:
        return False

    # Sortowanie klocków (bez jokerów)
    non_jokers = sorted([tile for tile in tiles if tile != JOKER])

    # Sprawdzenie koloru
    main_color = non_jokers[0].color
    if not all(tile.color == main_color for tile in non_jokers):
        return False

    # Sprawdzenie unikalności numerów (bez jokerów)
    if len(non_jokers) != len(set(non_jokers)):
        return False

    # Sprawdzenie sekwencji numerów z uwzględnieniem jokerów
    num_jokers = tiles.count(JOKER)
    expected_number = non_jokers[0].number

    for tile in non_jokers:
        diff = tile.number - expected_number
        if diff < 0 or diff > num_jokers:  # Przeskok jest zbyt duży, by wypełnić go jokerami
            return False
        num_jokers -= diff  # "Zużywamy" jokery na wypełnienie luki
        expected_number = tile.number + 1

    return True

def is_valid_meld(tiles: List[Tile]) -> bool:
    """Sprawdza, czy układ jest poprawną grupą LUB szeregiem."""
    return is_valid_group(tiles) or is_valid_run(tiles)

def is_table_valid(table: List[List[Tile]]) -> bool:
    """Sprawdza, czy cały stół jest poprawny."""
    if not table:
        return True
    return all(is_valid_meld(meld) for meld in table)
