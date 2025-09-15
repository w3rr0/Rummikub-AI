#ifndef SOLVER_H
#define SOLVER_H

#include "tile.h"
#include <vector>
#include <set>


std::vector<std::vector<std::vector<Tile>>>
find_all_valid_moves_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table,
    bool first_only
);

std::vector<std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>>
possible_moves_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table,
    const size_t max_target = 0
);

std::pair<std::vector<Tile>, std::vector<Tile>>
pre_filter_unplayable_tiles_cpp(
    const std::vector<Tile>& hand,
    const std::vector<std::vector<Tile>>& table
);


std::vector<std::vector<Tile>> get_combinations(const std::vector<Tile>& tiles, int r);

std::set<std::vector<Tile>> generate_all_possible_melds(const std::vector<Tile>& tiles);

#endif //SOLVER_H