from typing import FrozenSet, List, Set
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


def find_all_valid_moves(hand: Set[Tile], table: List[List[Tile]]) -> List[List[List[Tile]]]:
    """
    Główna funkcja, która znajduje wszystkie możliwe ruchy (nowe układy stołu).
    """
    initial_table_fset = frozenset(frozenset(meld) for meld in table)

    # Pula wszystkich klocków do ułożenia
    workspace_tiles = frozenset(hand.union(*[set(meld) for meld in table]))
    if not workspace_tiles:
        return []

    # Wstępne wygenerowanie wszystkich możliwych poprawnych sekwensów
    all_melds = generate_all_possible_melds(workspace_tiles)

    # Optymalizacja: Stwórz mapę {klocek -> [sekwensy, które go zawierają]}
    # To drastycznie przyspiesza wyszukiwanie w pętli rekurencyjnej.
    tile_to_melds_map = defaultdict(list)
    for meld in all_melds:
        for tile in meld:
            tile_to_melds_map[tile].append(meld)

    solutions = set()  # Tu będziemy przechowywać znalezione kompletne układy stołu

    def solve(tiles_to_cover: FrozenSet[Tile], current_layout: List[FrozenSet[Tile]]):
        """
        Funkcja rekurencyjna szukająca dokładnego pokrycia.
        """
        # --- Warunek bazowy: jeśli nie ma już klocków, znaleźliśmy rozwiązanie ---
        if not tiles_to_cover:
            # Using tuple to make the layout hashable
            solutions.add(frozenset(current_layout))
            return

        # --- Krok rekurencyjny ---
        # Wybierz jeden klocek do "pokrycia", aby zawęzić poszukiwania.
        # Wybranie najrzadszego (w najmniejszej liczbie sekwensów) to dobra heurystyka.
        # Dla prostoty wybierzmy po prostu pierwszy z brzegu.
        first_tile = next(iter(tiles_to_cover))

        # Iteruj przez wszystkie sekwensy, które mogą "pokryć" ten klocek
        for meld in tile_to_melds_map[first_tile]:
            # Sprawdź, czy ten sekwens można użyć (czy jego klocki są w puli do pokrycia)
            if meld.issubset(tiles_to_cover):
                # Jeśli tak, to rekurencyjnie szukaj dalej z mniejszą pulą klocków
                solve(tiles_to_cover - meld, current_layout + [meld])

    # Uruchomienie algorytmu
    solve(workspace_tiles, [])

    # Przetwarzanie unikalnych rozwiązań
    final_moves = []
    # solutions now contains tuples, which are hashable

    for layout in solutions:
        # Konwertuj z powrotem na listę list
        new_table = [list(meld) for meld in layout]

        # Sprawdź, czy ruch jest legalny:
        # 1. Nowy układ musi być inny niż początkowy
        # 2. Przynajmniej jeden klocek z ręki musiał zostać użyty
        new_table_fset = frozenset(frozenset(meld) for meld in new_table)
        tiles_in_new_table = {tile for meld in new_table for tile in meld}

        is_new_layout = (new_table_fset != initial_table_fset)
        uses_hand_tile = not hand.isdisjoint(tiles_in_new_table)

        if is_new_layout and uses_hand_tile:
            final_moves.append(new_table)

    return final_moves
