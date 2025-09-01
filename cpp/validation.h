#ifndef VALIDATION_H
#define VALIDATION_H

#include "tile.h"
#include <vector>

// Deklaracje funkcji, które będą implementowane w validation.cpp
bool is_valid_group(const std::vector<Tile>& tiles);
bool is_valid_run(std::vector<Tile> tiles); // Przekazywane przez wartość, bo sortujemy
bool is_valid_meld(const std::vector<Tile>& tiles);

#endif // VALIDATION_H