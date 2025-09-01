#include "solver.h"
#include "validation.h"
#include "tile.h"
#include <unordered_map>
#include <set>
#include <algorithm>
#include <functional>
#include <map>
#include <numeric>


std::vector<std::vector<Tile>> get_combinations(const std::vector<Tile>& tiles, int r) {
    if (r <= 0 || r > tiles.size()) {
        return {};
    }
    std::vector<std::vector<Tile>> result;
    std::vector<bool> v(tiles.size());
    std::fill(v.begin() + v.size() - r, v.end(), true);
    do {
        std::vector<Tile> combo;
        for (int i = 0; i < tiles.size(); ++i) {
            if (v[i]) {
                combo.push_back(tiles[i]);
            }
        }
        result.push_back(combo);
    } while (std::next_permutation(v.begin(), v.end()));
    return result;
}

std::set<std::vector<Tile>> generate_all_possible_melds(const std::vector<Tile>& tiles) {
    std::set<std::vector<Tile>> possible_melds;
    std::map<Tile, int> tile_counts;
    for(const auto& tile : tiles) {
        tile_counts[tile]++;
    }

    std::vector<Tile> unique_tiles_for_groups;
    for (const auto& pair : tile_counts) {
        unique_tiles_for_groups.push_back(pair.first);
    }
    for (int r = 3; r <= 4; ++r) {
        if (unique_tiles_for_groups.size() < r) continue;
        std::vector<std::vector<Tile>> combos = get_combinations(unique_tiles_for_groups, r);
        for (auto& combo : combos) {
            std::sort(combo.begin(), combo.end());
            if (is_valid_group(combo)) {
                possible_melds.insert(combo);
            }
        }
    }

    std::map<TileColor, std::vector<Tile>> tiles_by_color;
    std::vector<Tile> jokers;
    for(const auto& tile : tiles) {
        if(tile.color == TileColor::Joker) {
            jokers.push_back(tile);
        } else {
            tiles_by_color[tile.color].push_back(tile);
        }
    }

    for(auto const& [color, color_tiles_vec] : tiles_by_color) {
        std::vector<Tile> unique_non_jokers = color_tiles_vec;
        std::sort(unique_non_jokers.begin(), unique_non_jokers.end());
        unique_non_jokers.erase(std::unique(unique_non_jokers.begin(), unique_non_jokers.end()), unique_non_jokers.end());

        for (int r_tiles = 1; r_tiles <= unique_non_jokers.size(); ++r_tiles) {
            std::vector<std::vector<Tile>> tile_subsets = get_combinations(unique_non_jokers, r_tiles);
            for (const auto& tile_subset : tile_subsets) {
                for (int r_jokers = 0; r_jokers <= jokers.size(); ++r_jokers) {
                    if (r_jokers + r_tiles < 3) continue;
                    std::vector<std::vector<Tile>> joker_subsets = get_combinations(jokers, r_jokers);
                    if (joker_subsets.empty() && r_jokers == 0) {
                         std::vector<Tile> run_candidate = tile_subset;
                         std::sort(run_candidate.begin(), run_candidate.end());
                         if (is_valid_run(run_candidate)) {
                             possible_melds.insert(run_candidate);
                         }
                    } else {
                        for (const auto& joker_subset : joker_subsets) {
                            std::vector<Tile> run_candidate = tile_subset;
                            run_candidate.insert(run_candidate.end(), joker_subset.begin(), joker_subset.end());
                            std::sort(run_candidate.begin(), run_candidate.end());
                            if (is_valid_run(run_candidate)) {
                                possible_melds.insert(run_candidate);
                            }
                        }
                    }
                }
            }
        }
    }
    return possible_melds;
}



std::set<std::vector<Tile>> canonical_layout(const std::vector<std::vector<Tile>>& layout) {
    std::set<std::vector<Tile>> canonical_set;
    for (auto meld : layout) {
        std::sort(meld.begin(), meld.end());
        canonical_set.insert(meld);
    }
    return canonical_set;
}

std::vector<std::vector<std::vector<Tile>>>
find_all_valid_moves_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table,
    bool first_only
) {
    // 1. Przygotowanie danych
    auto initial_table_canonical = canonical_layout(table);

    std::unordered_map<Tile, int> workspace_tiles_counter;
    for (const auto& tile : hand) workspace_tiles_counter[tile]++;

    std::unordered_map<Tile, int> table_tiles_counter;
    for (const auto& meld : table) {
        for (const auto& tile : meld) {
            workspace_tiles_counter[tile]++;
            table_tiles_counter[tile]++;
        }
    }

    if (workspace_tiles_counter.empty()) {
        return {};
    }

    std::vector<Tile> all_tiles_list;
    for(const auto& [tile, count] : workspace_tiles_counter) {
        for(int i = 0; i < count; ++i) all_tiles_list.push_back(tile);
    }

    auto all_melds_set = generate_all_possible_melds(all_tiles_list);
    std::vector<std::vector<Tile>> all_melds(all_melds_set.begin(), all_melds_set.end());

    std::unordered_map<Tile, std::vector<std::vector<Tile>>> tile_to_melds_map;
    for(const auto& meld : all_melds) {
        std::set<Tile> unique_tiles_in_meld(meld.begin(), meld.end());
        for(const auto& tile : unique_tiles_in_meld) {
            tile_to_melds_map[tile].push_back(meld);
        }
    }

    std::set<std::vector<std::vector<Tile>>> solutions;

    // 2. Rekurencyjne rozwiązywanie
    std::function<void(std::unordered_map<Tile, int>, std::vector<std::vector<Tile>>)> solve_recursive;
    solve_recursive = [&](
        std::unordered_map<Tile, int> tiles_to_cover,
        std::vector<std::vector<Tile>> current_layout
    ) {
        if (first_only && !solutions.empty()) {
            return;
        }

        if (tiles_to_cover.empty()) {
            for(auto& meld : current_layout) std::sort(meld.begin(), meld.end());
            std::sort(current_layout.begin(), current_layout.end());
            solutions.insert(current_layout);
            return;
        }

        Tile tile_to_process;
        int min_melds = -1;

        for (const auto& pair : tiles_to_cover) {
            int current_melds_count = tile_to_melds_map.count(pair.first) ? tile_to_melds_map.at(pair.first).size() : 0;
            if (min_melds == -1 || current_melds_count < min_melds) {
                min_melds = current_melds_count;
                tile_to_process = pair.first;
            }
        }

        if(tile_to_melds_map.find(tile_to_process) == tile_to_melds_map.end()) {
            return;
        }

        for (const auto& meld : tile_to_melds_map.at(tile_to_process)) {
            std::unordered_map<Tile, int> meld_counter;
            for (const auto& t : meld) meld_counter[t]++;

            bool is_subset = true;
            for (const auto& pair : meld_counter) {
                auto it = tiles_to_cover.find(pair.first);
                if (it == tiles_to_cover.end() || it->second < pair.second) {
                    is_subset = false;
                    break;
                }
            }

            if (is_subset) {
                std::unordered_map<Tile, int> new_tiles_to_cover = tiles_to_cover;
                for (const auto& pair : meld_counter) {
                    new_tiles_to_cover[pair.first] -= pair.second;
                    if (new_tiles_to_cover[pair.first] == 0) {
                        new_tiles_to_cover.erase(pair.first);
                    }
                }
                std::vector<std::vector<Tile>> new_layout = current_layout;
                new_layout.push_back(meld);
                solve_recursive(new_tiles_to_cover, new_layout);
            }
        }
    };

    solve_recursive(workspace_tiles_counter, {});

    std::vector<std::vector<std::vector<Tile>>> final_moves;
    for (const auto& layout : solutions) {
        auto new_table_canonical = canonical_layout(layout);

        bool is_new_layout = (new_table_canonical != initial_table_canonical);

        std::unordered_map<Tile, int> new_table_tiles_counter;
        for(const auto& meld : layout) {
            for(const auto& tile : meld) new_table_tiles_counter[tile]++;
        }

        int used_from_hand_count = 0;
        for(const auto& pair : new_table_tiles_counter) {
            int in_table = table_tiles_counter.count(pair.first) ? table_tiles_counter.at(pair.first) : 0;
            if(pair.second > in_table) {
                used_from_hand_count += pair.second - in_table;
            }
        }

        if (is_new_layout && used_from_hand_count > 0) {
            final_moves.push_back(layout);
            if (first_only) {
                return final_moves;
            }
        }
    }

    return final_moves;
}