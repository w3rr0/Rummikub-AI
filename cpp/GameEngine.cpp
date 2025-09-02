#include "GameEngine.h"
#include <algorithm>
#include <random>
#include <stdexcept>
#include <unordered_map>


GameState::GameState(int num_players, int blocks, int r)
    : players(num_players), current_player(0), done(false), winner(std::nullopt) {

    std::vector<Tile> tile_pull;
    for (const auto& color : {TileColor::Red, TileColor::Blue, TileColor::Yellow, TileColor::Black}) {
        for (int number = 1; number <= r; ++number) {
            tile_pull.emplace_back(number, color);
        }
    }
    tile_pull.insert(tile_pull.end(), tile_pull.begin(), tile_pull.end());
    tile_pull.emplace_back(1, TileColor::Joker);
    tile_pull.emplace_back(2, TileColor::Joker);

    stock = tile_pull;

    // Tasowanie
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(stock.begin(), stock.end(), g);

    // Rozdawanie
    hands.resize(players);
    for (int i = 0; i < players; ++i) {
        for (int j = 0; j < blocks; ++j) {
            if (stock.empty()) break;
            hands[i].push_back(stock.back());
            stock.pop_back();
        }
    }
}

GameState GameState::clone() const {
    GameState new_state(this->players);
    new_state.stock = this->stock;
    new_state.hands = this->hands;
    new_state.table = this->table;
    new_state.current_player = this->current_player;
    new_state.done = this->done;
    new_state.winner = this->winner;
    return new_state;
}


GameEngine::GameEngine(int players, int blocks_start, int blocks_range)
    : state(players, blocks_start, blocks_range) {}

std::vector<std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>>
GameEngine::enumerate_moves(int player) {
    if (player < 0 || player >= state.players) {
        throw std::out_of_range("Invalid player index");
    }
    const auto& hand = state.hands[player];
    const auto& table = state.table;

    auto moves = possible_moves_cpp(hand, table);

    if (moves.empty() || !state.stock.empty()) {
        moves.emplace_back(table, std::vector<Tile>{});
    }

    return moves;
}

void GameEngine::apply_move(int player, const std::tuple<std::vector<std::vector<Tile>>, std::vector<Tile>>& move) {
    if (player != state.current_player) {
        throw std::runtime_error("It is not this player's turn");
    }

    const auto& new_table = std::get<0>(move);
    const auto& used_tiles = std::get<1>(move);

    // Przypadek dobrania karty
    if (used_tiles.empty()) {
        if (!state.stock.empty()) {
            state.hands[player].push_back(state.stock.back());
            state.stock.pop_back();
        }
    } else {
        std::unordered_map<Tile, int> hand_counts;
        for(const auto& tile : state.hands[player]) {
            hand_counts[tile]++;
        }
        for(const auto& tile : used_tiles) {
            if(hand_counts[tile] == 0) {
                 throw std::runtime_error("Player does not have the required tile: " + std::to_string(tile.number));
            }
            hand_counts[tile]--;
        }

        std::vector<Tile> new_hand;
        for(const auto& pair : hand_counts) {
            for(int i = 0; i < pair.second; ++i) {
                new_hand.push_back(pair.first);
            }
        }
        state.hands[player] = new_hand;

        state.table = new_table;

        if (state.hands[player].empty()) {
            state.done = true;
            state.winner = player;
        }
    }

    if (!state.done) {
        state.current_player = (state.current_player + 1) % state.players;
    }
}