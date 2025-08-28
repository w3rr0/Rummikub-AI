from typing import FrozenSet, List, Set
from collections import defaultdict, Counter
from itertools import combinations

from game import Tile
from validation import is_valid_group, is_valid_run

def generate_all_possible_melds(tiles: FrozenSet[Tile]) -> List[FrozenSet[Tile]]:
    """Generuje wszystkie możliwe poprawne grupy i szeregi z danego zbioru klocków."""
    possible_melds = set()
    unique_tiles = list(tiles)

    # 1. Generuj grupy
    for r in range(3, 5): # Grupy mogą mieć 3 lub 4 klocki
        for group_candidate in combinations(unique_tiles, r):
            if is_valid_group(list(group_candidate)):
                possible_melds.add(frozenset(group_candidate))

    # 2. Generuj szeregi
    tiles_by_color = defaultdict(list)
    for tile in unique_tiles:
        tiles_by_color[tile.color].append(tile)

    for color in tiles_by_color:
        sorted_tiles = sorted(tiles_by_color[color])
        if len(sorted_tiles) >= 3:
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
    all_tiles_list = list(hand) + [tile for meld in table for tile in meld]
    workspace_tiles_counter = Counter(all_tiles_list)

    if not workspace_tiles_counter:
        return []

    # Wstępne wygenerowanie wszystkich możliwych poprawnych sekwensów
    unique_tiles = frozenset(workspace_tiles_counter.keys())
    all_melds = generate_all_possible_melds(unique_tiles)

    # Optymalizacja: Stwórz mapę {klocek -> [sekwensy, które go zawierają]}
    # To drastycznie przyspiesza wyszukiwanie w pętli rekurencyjnej.
    tile_to_melds_map = defaultdict(list)
    for meld in all_melds:
        for tile in meld:
            tile_to_melds_map[tile].append(meld)

    solutions = set()  # Tu będziemy przechowywać znalezione kompletne układy stołu

    def solve(tiles_to_cover: Counter[Tile], current_layout: List[FrozenSet[Tile]]):
        """
        Funkcja rekurencyjna szukająca dokładnego pokrycia.
        """
        # --- Warunek bazowy: jeśli nie ma już klocków, znaleźliśmy rozwiązanie ---
        if not tiles_to_cover:
            # Using tuple to make the layout hashable
            sorted_layout = tuple(tuple(sorted(list(meld))) for meld in current_layout)
            solutions.add(tuple(sorted(sorted_layout)))  # Sortujemy też całą listę meldów
            return

        # --- Krok rekurencyjny ---
        # Wybierz jeden klocek do "pokrycia", aby zawęzić poszukiwania.
        # Wybranie najrzadszego (w najmniejszej liczbie sekwensów) to dobra heurystyka.
        # Dla prostoty wybierzmy po prostu pierwszy z brzegu.
        first_tile = next(iter(tiles_to_cover.keys()))

        # Iteruj przez wszystkie sekwensy, które mogą "pokryć" ten klocek
        for meld in tile_to_melds_map[first_tile]:
            meld_counter = Counter(meld)

            can_form_meld = all(tiles_to_cover[tile] >= meld_counter[tile] for tile in meld)

            if can_form_meld:
                remaining_tiles = tiles_to_cover - meld_counter
                solve(remaining_tiles, current_layout + [meld])

    # Uruchomienie algorytmu
    solve(workspace_tiles_counter, [])

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
        tiles_in_new_table_counter = Counter(tile for meld in new_table for tile in meld)

        is_new_layout = (new_table_fset != initial_table_fset)
        uses_hand_tile = any(tile in tiles_in_new_table_counter for tile in hand)

        if is_new_layout and uses_hand_tile:
            final_moves.append(new_table)

    return final_moves
