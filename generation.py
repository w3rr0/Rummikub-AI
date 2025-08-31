from typing import List, Tuple
from collections import defaultdict, Counter
from itertools import combinations

from tile import Tile
from validation import is_valid_group, is_valid_run


def generate_all_possible_melds(tiles: List[Tile]) -> List[Tuple[Tile]]:
    """Generuje wszystkie możliwe poprawne grupy i szeregi z danego zbioru klocków."""
    possible_melds = set()

    # 1. Generuj grupy
    for r in range(3, 5): # Grupy mogą mieć 3 lub 4 klocki
        for group_candidate_tuple in combinations(tiles, r):
            group_candidate = list(group_candidate_tuple)
            if is_valid_group(group_candidate):
                possible_melds.add(tuple(sorted(group_candidate)))

    # 2. Generuj szeregi
    tiles_by_color = defaultdict(list)
    jokers = [t for t in tiles if t.color == 'Joker']
    non_jokers = [t for t in tiles if t.color != 'Joker']

    for tile in non_jokers:
        tiles_by_color[tile.color].append(tile)

    for color in tiles_by_color:
        color_tiles = sorted(list(set(tiles_by_color[color])))
        for r_tiles in range(1, len(color_tiles) + 1):
            for tile_subset_tuple in combinations(color_tiles, r_tiles):
                for r_jokers in range(len(jokers) + 1):
                    if r_jokers > len(jokers):
                        continue
                    for joker_subset_tuple in combinations(jokers, r_jokers):
                        if len(tile_subset_tuple) + len(joker_subset_tuple) < 3:
                            continue

                        run_candidate = list(tile_subset_tuple) + list(joker_subset_tuple)
                        if is_valid_run(run_candidate):
                            possible_melds.add(tuple(sorted(run_candidate)))

    return list(possible_melds)


def pre_filter_unplayable_tiles(hand: List[Tile], table: List[List[Tile]]) -> Tuple[List[Tile], List[Tile]]:
    if not hand:
        return [], []

    pool = hand + [tile for meld in table for tile in meld]
    pool_counter = Counter(pool)
    joker_count = sum(count for tile, count in pool_counter.items() if tile.color == 'Joker')

    playable_hand = []
    unplayable_hand = []

    for tile, count in Counter(hand).items():
        if tile.color == 'Joker':
            playable_hand.extend([tile]*count)
            continue

        is_playable = False

        pool_counter[tile] -= 1

        colors_to_check = {'Red', 'Blue', 'Yellow', 'Black'}
        if tile.color in colors_to_check:
            colors_to_check.discard(tile.color)

        same_number_partners = 0
        for color in colors_to_check:
            same_number_partners += pool_counter.get(Tile(tile.number, color), 0)

        if (same_number_partners + joker_count) >= 2:
            is_playable = True

        if not is_playable:
            num, color = tile.number, tile.color

            # Kombinacja [N-2, N-1, N]
            needed1, needed2 = Tile(num - 1, color), Tile(num - 2, color)
            if (pool_counter.get(needed1, 0) + pool_counter.get(needed2, 0) + joker_count) >= 2:
                is_playable = True

            # Kombinacja [N-1, N, N+1]
            if not is_playable:
                needed1, needed2 = Tile(num - 1, color), Tile(num + 1, color)
                if (pool_counter.get(needed1, 0) + pool_counter.get(needed2, 0) + joker_count) >= 1:
                    is_playable = True

            if not is_playable:
                needed1, needed2 = Tile(num + 1, color), Tile(num + 2, color)
                if (pool_counter.get(needed1, 0) + pool_counter.get(needed2, 0) + joker_count) >= 2:
                    is_playable = True

        pool_counter[tile] += 1

        if is_playable:
            playable_hand.extend([tile] * count)
        else:
            unplayable_hand.extend([tile] * count)

    return playable_hand, unplayable_hand


def find_all_valid_moves(hand: List[Tile], table: List[List[Tile]], first_only=False) -> List[List[List[Tile]]]:
    """
    Główna funkcja, która znajduje wszystkie możliwe ruchy (nowe układy stołu).
    """
    initial_table_fset = frozenset(frozenset(meld) for meld in table)

    # Pula wszystkich klocków do ułożenia
    all_tiles_list = hand + [tile for meld in table for tile in meld]
    workspace_tiles_counter = Counter(all_tiles_list)

    if not workspace_tiles_counter:
        return []

    all_melds = generate_all_possible_melds(all_tiles_list)

    tile_to_melds_map = defaultdict(list)
    for meld in all_melds:
        for tile in set(meld):
            tile_to_melds_map[tile].append(meld)

    solutions = set()

    def solve(tiles_to_cover: Counter[Tile], current_layout: List[Tuple[Tile]]):
        """
        Funkcja rekurencyjna szukająca dokładnego pokrycia.
        """
        if first_only and solutions:
            return
        if not tiles_to_cover:
            solutions.add(tuple(sorted(current_layout)))
            return

        tile_to_process = min(tiles_to_cover.keys(), key=lambda t: len(tile_to_melds_map.get(t, [1]*1000)))

        for meld in tile_to_melds_map[tile_to_process]:
            meld_counter = Counter(meld)
            if all(tiles_to_cover[tile] >= meld_counter[tile] for tile in meld):
                solve(tiles_to_cover - meld_counter, current_layout + [meld])

    solve(workspace_tiles_counter, [])

    final_moves = []

    for layout in solutions:
        new_table = [list(meld) for meld in layout]

        new_table_fset = frozenset(frozenset(meld) for meld in new_table)

        is_new_layout = new_table_fset != initial_table_fset

        table_tiles_counter = Counter(tile for meld in table for tile in meld)
        new_table_tiles_counter = Counter(tile for meld in new_table for tile in meld)

        if len(new_table_tiles_counter) < len(table_tiles_counter):
            continue

        used_from_hand_counter = new_table_tiles_counter - table_tiles_counter

        if is_new_layout and sum(used_from_hand_counter.values()) > 0:
            final_moves.append(new_table)
            if first_only:
                return final_moves

    return final_moves


def possible_moves(hand: List[Tile], table: List[List[Tile]]) -> List[Tuple[List[List[Tile]], List[Tile]]]:
    """
    Returns all possible new table setups,
    where each table setup is a list of all groups,
    which are lists of tiles belonging to that group

    :param hand:
    :param table:
    :return:
    """
    playable_hand, _ = pre_filter_unplayable_tiles(hand, table)
    if not playable_hand:
        return []

    all_found_moves = []
    seen_tables = set()

    for r in range(1, len(playable_hand) + 1):
        for combo in combinations(playable_hand, r):
            used_hand_tiles = list(combo)

            solution_for_combo = find_all_valid_moves(used_hand_tiles, table, True)

            if solution_for_combo:
                solution = solution_for_combo[0]
                table_signature = frozenset(frozenset(meld) for meld in solution)
                if table_signature not in seen_tables:
                    all_found_moves.append((solution, used_hand_tiles))
                    seen_tables.add(table_signature)

    return all_found_moves
