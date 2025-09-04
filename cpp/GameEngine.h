#ifndef GAME_LOGIC_H
#define GAME_LOGIC_H

#include "tile.h"
#include "solver.h"
#include <vector>
#include <optional>
#include <tuple>

class GameState {
public:
    std::vector<Tile> stock;
    std::vector<std::vector<Tile>> hands;
    std::vector<std::vector<Tile>> table;
    int players;
    int current_player;
    bool done;
    std::optional<int> winner;
    bool player_putted;

    GameState(int num_players, int blocks = 14, int r = 13);

    GameState clone() const;
};

class GameEngine {
public:
    GameState state;

    GameEngine(int players = 2, int blocks_start = 14, int blocks_range = 13);

    std::vector<std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>> enumerate_moves(int player);

    void apply_move(int player, const std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>& move);

    void next_player(bool placed);
};

#endif // GAME_LOGIC_H