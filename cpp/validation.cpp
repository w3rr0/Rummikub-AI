#include "validation.h"
#include <vector>
#include <numeric>
#include <algorithm>
#include <unordered_set>

bool is_valid_group(const std::vector<Tile>& tiles) {
    if (tiles.size() < 3 || tiles.size() > 4) return false;

    std::vector<Tile> non_jokers;
    for (const auto& tile : tiles) {
        if (tile.color != TileColor::Joker) {
            non_jokers.push_back(tile);
        }
    }

    if (!non_jokers.empty()) {
        int first_number = non_jokers[0].number;
        for (const auto& tile : non_jokers) {
            if (tile.number != first_number) return false;
        }
    }

    std::unordered_set<TileColor> colors;
    for (const auto& tile : non_jokers) {
        if (colors.count(tile.color)) return false;
        colors.insert(tile.color);
    }

    return true;
}


bool is_valid_run(std::vector<Tile> tiles) {
    if (tiles.size() < 3) return false;

    std::vector<Tile> non_jokers;
    for (const auto& tile : tiles) {
        if (tile.color != TileColor::Joker) {
            non_jokers.push_back(tile);
        }
    }

    if (non_jokers.empty()) return true;

    std::sort(non_jokers.begin(), non_jokers.end());

    TileColor main_color = non_jokers[0].color;
    std::unordered_set<int> numbers;
    for (const auto& tile : non_jokers) {
        if (tile.color != main_color) return false;
        if (numbers.count(tile.number)) return false;
        numbers.insert(tile.number);
    }

    int min_num = non_jokers.front().number;
    int max_num = non_jokers.back().number;

    return (max_num - min_num + 1) <= tiles.size();
}


bool is_valid_meld(const std::vector<Tile>& tiles) {
    return is_valid_group(tiles) || is_valid_run(tiles);
}