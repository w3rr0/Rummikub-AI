import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Literal

from game import GameEngine as GEP
from rummikub_solver import GameEngine as GEC
from rummikub_solver import TileColor as TCC

versions = Literal["cpp", "python"]
class TCP:
    Red = "Red"
    Blue = "Blue"
    Yellow = "Yellow"
    Black = "Black"
    Joker = "Joker"

# Default game engine
GameEngine = GEC
Color = TCC

class RummikubEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, players: int = 2, blocks_start: int = 14, blocks_range: int = 13, version: versions = "cpp"):
        super().__init__()
        global GameEngine, Color
        match(version):
            case "cpp":
                GameEngine = GEC
                Color = TCC
            case "python":
                GameEngine = GEP
                Color = TCP
        self.players = players
        self.engine = GameEngine(players, blocks_start, blocks_range)

        self.number_of_tiles = blocks_range * 4 * 2 + 2
        self.observation_space = spaces.Box(
            low=0, high=2, shape=(self.number_of_tiles,), dtype=np.int32
        )

        self.max_actions = 100
        self.action_space = spaces.Discrete(self.max_actions)

        self.blocks_start = blocks_start
        self.blocks_range = blocks_range

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        global GameEngine
        self.engine = GameEngine(self.players, self.blocks_start, self.blocks_range)
        obs = self._get_obs()
        return obs, {}

    def step(self, action: int):
        player = self.engine.state.current_player
        moves = self.engine.enumerate_moves(player)

        if action >= len(moves):
            move = (self.engine.state.table, [])
        else:
            move = moves[action]

        self.engine.apply_move(player, move)

        obs = self._get_obs()
        reward = self._get_reward(player, move)
        terminated = self.engine.state.done
        truncated = False   # Limit ruchów (brak)
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self, mode="human"):
        print(f"\n--- Player {self.engine.state.current_player} ---")
        for i, hand in enumerate(self.engine.state.hands):
            print(f"Player {i} hand: {hand}")
        print(f"Table: {self.engine.state.table}")

    def _get_obs(self):
        """
        Zamiana stanu gry na wektor liczb (obserwacja dla sieci NN).
        Każdy typ kafelka = unikalny indeks (0..105).
        """
        all_tiles = self.engine.state.hands[self.engine.state.current_player] + [
            tile for meld in self.engine.state.table for tile in meld
        ]
        vec = np.zeros(self.number_of_tiles, dtype=np.int32)

        # indeks = kolor * liczba kafelków + (numer-1), jokery na końcu
        def tile_to_idx(tile):
            color_idx = {Color.Red: 0, Color.Blue: 1, Color.Yellow: 2, Color.Black: 3, Color.Joker: 4}[tile.color]
            return color_idx * self.blocks_range + (tile.number - 1)

        for t in all_tiles:
            vec[tile_to_idx(t)] += 1

        return vec

    def _get_reward(self, player, move):
        """
        Bardzo prosty shaping nagrody:
        + za zagrane kafle, -0.1 za PASS, +100/-100 za win/loss
        """
        _, used_tiles = move
        reward = len(used_tiles)

        if len(used_tiles) == 0:
            reward -= 0.1

        if self.engine.state.done:
            if self.engine.state.winner == player:
                reward += 100
            else:
                reward -= 100

        return reward
