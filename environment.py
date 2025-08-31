import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game import GameEngine, GameState

class RummikubEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, players: int = 2, blocks_start: int = 14, blocks_range: int = 14):
        super().__init__()
        self.players = players
        self.engine = GameEngine(players, blocks_start, blocks_range)

        # Observation = ręka + stół
        # uproszczenie: wektor długości 106 (liczba każdego rodzaju kafelka)
        self.observation_space = spaces.Box(
            low=0, high=2, shape=(106,), dtype=np.int32
        )

        # Action = wybór indeksu ruchu z enumerate_moves
        # Maksymalna liczba ruchów to np. 100 (resztę potraktujemy jako "no-op")
        self.max_actions = 100
        self.action_space = spaces.Discrete(self.max_actions)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.engine = GameEngine(self.players)
        obs = self._get_obs()
        return obs, {}

    def step(self, action: int):
        player = self.engine.state.current_player
        moves = self.engine.enumerate_moves(player)

        # jeśli akcja > dostępne ruchy → PASS
        if action >= len(moves):
            move = (self.engine.state.table, [])
        else:
            move = moves[action]

        self.engine.apply_move(player, move)

        obs = self._get_obs()
        reward = self._get_reward(player, move)
        terminated = self.engine.state.done
        truncated = False  # brak limitu ruchów
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
        vec = np.zeros(106, dtype=np.int32)

        # indeks = kolor*13 + (numer-1), jokery na końcu
        def tile_to_idx(tile):
            if tile.color == "Joker":
                return 104 + tile.number  # dwa jokery
            color_idx = {"Red": 0, "Blue": 1, "Yellow": 2, "Black": 3}[tile.color]
            return color_idx * 13 + (tile.number - 1)

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
