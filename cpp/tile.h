#ifndef TILE_H
#define TILE_H

#include <functional> // Dla std::hash

// Odpowiednik TileColor z Pythona
enum class TileColor { Red, Blue, Yellow, Black, Joker };

// Struktura Tile
struct Tile {
    int number;
    TileColor color;

    bool operator==(const Tile& other) const {
        return number == other.number && color == other.color;
    }

    bool operator<(const Tile& other) const {
        if (number != other.number) {
            return number < other.number;
        }
        return color < other.color;
    }
};

namespace std {
    template <>
    struct hash<Tile> {
        size_t operator()(const Tile& t) const {
            size_t h1 = hash<int>()(t.number);
            size_t h2 = hash<int>()(static_cast<int>(t.color));
            return h1 ^ (h2 << 1);
        }
    };
}

#endif // TILE_H