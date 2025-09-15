#include "solver.h"
#include "validation.h"
#include "tile.h"
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
        if (tiles.size() < r) continue;
        std::vector<std::vector<Tile>> combos = get_combinations(tiles, r);
        for (auto& combo : combos) {
            if (is_valid_group(combo)) {
                std::sort(combo.begin(), combo.end());
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
    auto initial_table_canonical = canonical_layout(table);

    std::map<Tile, int> workspace_tiles_counter;
    for (const auto& tile : hand) workspace_tiles_counter[tile]++;

    std::map<Tile, int> table_tiles_counter;
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

    std::map<Tile, std::vector<std::vector<Tile>>> tile_to_melds_map;
    for(const auto& meld : all_melds) {
        std::set<Tile> unique_tiles_in_meld(meld.begin(), meld.end());
        for(const auto& tile : unique_tiles_in_meld) {
            tile_to_melds_map[tile].push_back(meld);
        }
    }

    std::set<std::vector<std::vector<Tile>>> solutions;

    std::function<void(std::map<Tile, int>, std::vector<std::vector<Tile>>)> solve_recursive;
    solve_recursive = [&](
        std::map<Tile, int> tiles_to_cover,
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
            std::map<Tile, int> meld_counter;
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
                std::map<Tile, int> new_tiles_to_cover = tiles_to_cover;
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

        std::map<Tile, int> new_table_tiles_counter;
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

std::vector<std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>>
possible_moves_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table,
    const size_t max_target
) {
    auto filtered_hands = pre_filter_unplayable_tiles_cpp(hand, table);
    const auto& playable_hand = filtered_hands.first;

    if (playable_hand.empty()) {
        return {};
    }

    std::vector<std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>> all_found_moves;
    std::set<std::vector<std::vector<Tile>>> seen_tables;

    size_t target
    if (max_target) {
        target = std::min(max_target, playable_hand.size())
    } else {
        target = playable_hand.size();
    }

    for (size_t r = 1; r <= target; ++r) {
        std::vector<std::vector<Tile>> combinations_of_hand = get_combinations(playable_hand, r);

        for (const auto& combo : combinations_of_hand) {
            std::vector<Tile> used_hand_tiles = combo;

            std::vector<std::vector<std::vector<Tile>>> solution_for_combo =
                find_all_valid_moves_cpp(used_hand_tiles, table, true);

            if (!solution_for_combo.empty()) {
                std::vector<std::vector<Tile>> solution = solution_for_combo[0];

                std::vector<std::vector<Tile>> sorted_solution = solution;
                for(auto& meld : sorted_solution) {
                    std::sort(meld.begin(), meld.end());
                }
                std::sort(sorted_solution.begin(), sorted_solution.end());

                if (seen_tables.find(sorted_solution) == seen_tables.end()) {
                    all_found_moves.emplace_back(solution, used_hand_tiles);
                    seen_tables.insert(sorted_solution);
                }
            }
        }
    }

    return all_found_moves;
}


std::pair<std::vector<Tile>, std::vector<Tile>>
pre_filter_unplayable_tiles_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table
) {
    if (hand.empty()) {
        return {std::vector<Tile>(), std::vector<Tile>()};
    }

    std::map<Tile, int> pool_counter;
    int joker_count = 0;

    for (const auto& tile : hand) {
        if (tile.color == TileColor::Joker) {
            joker_count++;
        } else {
            pool_counter[tile]++;
        }
    }
    for (const auto& meld : table) {
        for (const auto& tile : meld) {
            if (tile.color == TileColor::Joker) {
                joker_count++;
            } else {
                pool_counter[tile]++;
            }
        }
    }

    std::vector<Tile> playable_hand;
    std::vector<Tile> unplayable_hand;

    std::map<Tile, int> hand_counter;
    for (const auto& tile : hand) {
        hand_counter[tile]++;
    }

    for (const auto& pair : hand_counter) {
        const auto& tile = pair.first;
        const int count = pair.second;

        if (tile.color == TileColor::Joker) {
            for (int i = 0; i < count; ++i) {
                playable_hand.push_back(tile);
            }
            continue;
        }

        bool is_playable = false;

        pool_counter[tile]--;

        int same_number_partners = 0;
        std::vector<TileColor> colors_to_check = {TileColor::Red, TileColor::Blue, TileColor::Yellow, TileColor::Black};

        for (const auto& color : colors_to_check) {
            if(color != tile.color) {
                same_number_partners += pool_counter.count(Tile(tile.number, color)) ? pool_counter.at(Tile(tile.number, color)) : 0;
            }
        }

        if ((same_number_partners + joker_count) >= 2) {
            is_playable = true;
        }

        if (!is_playable) {

            int needed1_count;
            int needed2_count;

            // Kombinacja [N-2, N-1, N]
            needed1_count = pool_counter.count(Tile(tile.number - 1, tile.color)) ? pool_counter.at(Tile(tile.number - 1, tile.color)) : 0;
            needed2_count = pool_counter.count(Tile(tile.number - 2, tile.color)) ? pool_counter.at(Tile(tile.number - 2, tile.color)) : 0;
            if ((needed1_count + needed2_count + joker_count) >= 2) {
                is_playable = true;
            }

            // Kombinacja [N-1, N, N+1]
            if (!is_playable) {
                needed1_count = pool_counter.count(Tile(tile.number - 1, tile.color)) ? pool_counter.at(Tile(tile.number - 1, tile.color)) : 0;
                needed2_count = pool_counter.count(Tile(tile.number + 1, tile.color)) ? pool_counter.at(Tile(tile.number + 1, tile.color)) : 0;
                if ((needed1_count + needed2_count + joker_count) >= 2) {
                    is_playable = true;
                }
            }

            // Kombinacja [N, N+1, N+2]
            if (!is_playable) {
                needed1_count = pool_counter.count(Tile(tile.number + 1, tile.color)) ? pool_counter.at(Tile(tile.number + 1, tile.color)) : 0;
                needed2_count = pool_counter.count(Tile(tile.number + 2, tile.color)) ? pool_counter.at(Tile(tile.number + 2, tile.color)) : 0;
                if ((needed1_count + needed2_count + joker_count) >= 2) {
                    is_playable = true;
                }
            }
        }

        pool_counter[tile]++;

        if (is_playable) {
            for (int i = 0; i < count; ++i) {
                playable_hand.push_back(tile);
            }
        } else {
            for (int i = 0; i < count; ++i) {
                unplayable_hand.push_back(tile);
            }
        }
    }

    return {playable_hand, unplayable_hand};
}