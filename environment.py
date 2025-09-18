from itertools import combinations
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Literal, List
from enum import Enum


from game import GameEngine as GEP
from rummikub_solver import GameEngine as GEC
from rummikub_solver import TileColor as TCC

from tile import Tile as TP
from rummikub_solver import Tile as TC

versions = Literal["cpp", "python"]
class TCP(str, Enum):
    Red = "Red"
    Blue = "Blue"
    Yellow = "Yellow"
    Black = "Black"
    Joker = "Joker"

# Default game engine
GameEngine = GEC
Color = TCC
Tile = TC

class RummikubEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, players: int = 2, blocks_start: int = 14, blocks_range: int = 13, version: versions = "cpp", render_mask: bool = True):
        super().__init__()
        global GameEngine, Color, Tile
        match(version):
            case "cpp":
                GameEngine = GEC
                Color = TCC
                Tile = TC
            case "python":
                GameEngine = GEP
                Color = TCP
                Tile = TP

        self.version = version
        self.players = players
        self.engine = GameEngine(players, blocks_start, blocks_range)
        self.render_mask = render_mask

        self.number_of_tiles = blocks_range * 4 * 2 + 2
        self.observation_space = spaces.Box(
            low=0, high=2, shape=(self.number_of_tiles,), dtype=np.int32
        )

        self.actions = []

        # combinations of 1
        for num in range(1, blocks_range + 1):
            self.actions.append((Tile(num, Color.Red), ))
            self.actions.append((Tile(num, Color.Blue), ))
            self.actions.append((Tile(num, Color.Yellow), ))
            self.actions.append((Tile(num, Color.Black), ))
        self.actions.append((Tile(1, Color.Joker), ))

        # combinations of 2
        self.actions.extend(list(combinations(self.actions, 2)))
        for num in range(1, blocks_range + 1):
            for color in [Color.Red, Color.Blue, Color.Yellow, Color.Black]:
                self.actions.append((Tile(num, color), Tile(num, color)))

        # combinations of 3
        # runs
        for num in range(1, blocks_range - 1):
            for color in [Color.Red, Color.Blue, Color.Yellow, Color.Black]:
                if color != Color.Joker:
                    # without jokers
                    self.actions.append((Tile(num, color), Tile(num + 1, color), Tile(num + 2, color)))
                    # with 1 joker
                    self.actions.append((Tile(num, color), Tile(1, Color.Joker), Tile(num + 2, color)))
        # with 1 joker
        for num in range(1, blocks_range):
            for color in [Color.Red, Color.Blue, Color.Yellow, Color.Black]:
                if color != Color.Joker:
                    self.actions.append((Tile(num, color), Tile(num + 1, color), Tile(1, Color.Joker)))
        # with 2 jokers included in melds with 2 jokers
        # melds
        for num in range(1, blocks_range + 1):
            # without jokers
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Blue), Tile(num, Color.Yellow)))
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Blue), Tile(num, Color.Black)))
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Black), Tile(num, Color.Yellow)))
            self.actions.append((Tile(num, Color.Black), Tile(num, Color.Blue), Tile(num, Color.Yellow)))
            # with 1 joker
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Blue), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Yellow), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Red), Tile(num, Color.Black), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Blue), Tile(num, Color.Yellow), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Blue), Tile(num, Color.Black), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Yellow), Tile(num, Color.Black), Tile(1, Color.Joker)))
            # with 2 jokers
            self.actions.append((Tile(num, Color.Red), Tile(1, Color.Joker), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Blue), Tile(1, Color.Joker), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Yellow), Tile(1, Color.Joker), Tile(1, Color.Joker)))
            self.actions.append((Tile(num, Color.Black), Tile(1, Color.Joker), Tile(1, Color.Joker)))


        self.max_actions = len(self.actions) + 2 # all possible combinations + PASS + DRAW
        self.action_space = spaces.Discrete(self.max_actions)

        self.blocks_start = blocks_start
        self.blocks_range = blocks_range

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        global GameEngine
        self.engine = GameEngine(self.players, self.blocks_start, self.blocks_range)
        obs = self._get_obs()
        if self.render_mask:
            mask = self._get_mask()
        else:
            mask = None
        return obs, {"action_mask": mask}

    def step(self, action: int):
        player = self.engine.state.current_player
        moves = self.engine.enumerate_moves(player)
        print("CHOSEN ACTION:", action)

        if action >= self.max_actions:
            raise ValueError("Out-of-scope action")
        # 0 - placed; 1 - draw
        elif 0 <= action <= 1:
            placed = action == 0
            self.engine.next_player(placed=placed)
        else:
            tiles: tuple = self.actions[action - 2]
            tiles_key = self._tiles_to_key(tiles)
            if self.version == "cpp":
                move = next((m for m in moves if self._tiles_to_key(m[1]) == tiles_key), None)
            elif self.version == "python":
                move = next((m for m in moves if tuple(m[1], ) == tiles), None)
            self.engine.apply_move(player, move)
            self.engine.state.player_putted = True

        obs = self._get_obs()
        reward = self._get_reward(player, action)
        terminated = self.engine.state.done
        truncated = False   # Limit ruchów (brak)
        if self.render_mask:
            mask = self._get_mask()
        else:
            mask = None

        return obs, reward, terminated, truncated, {"action_mask": mask}

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


    def _get_mask(self) -> List[int]:
        player = self.engine.state.current_player
        possible_moves = self.engine.enumerate_moves(player)

        legal_moves = [tuple(move[1]) for move in possible_moves]


        # gracz wystawil sie
        if self.engine.state.player_putted:
            PASS = 1
            DRAW = 0
        else:
            # gracz nie wystawił się i moze dobrac
            if self.engine.state.stock:
                PASS = 0
                DRAW = 1
            else:
                # gracz nie wystawil sie i nie ma jak dobrac, ale ma inne ruchy
                if legal_moves:
                    PASS = 0
                    DRAW = 0
                # gracz nie wystawil sie i nie ma jak dobrac, nie ma innych ruchów
                else:
                    PASS = 1
                    DRAW = 0

        def normalize(move):
            return tuple(t if isinstance(t, Tile) else t[0] for t in move)


        mask = [PASS, DRAW]
        for action in self.actions:
            if not isinstance(action, tuple):
                action = tuple(action)
            if self.version == "cpp":
                mask.append(1 if normalize(action) in [normalize(m) for m in legal_moves] else 0)
            elif self.version == "python":
                mask.append(1 if action in legal_moves else 0)

        return mask

    def _get_reward(self, player, move: int):
        """
        Bardzo prosty shaping nagrody:
        + za zagrane kafle, -0.5 za PASS, +100/-100 za win/loss
        """

        reward = 0

        # PASS - does not change the reward
        # DRAW
        if move == 1:
            reward -= 0.5
        # PLACE
        elif move > 1:
            tiles: tuple = self.actions[move - 2]
            reward += len(tiles)

        if self.engine.state.done:
            if self.engine.state.winner == player:
                reward += 100
            else:
                reward -= 100

        return reward


    def _tiles_to_key(self, tile_seq):
        """Zamienia dowolną strukturę kafelków (Tile, (Tile,), [Tile], ((Tile,), ...))
           na spłaszczoną krotkę par (number, str(color)) zachowując kolejność."""
        vals = []
        def collect(x):
            # list/tuple => iteruj i rekurencyjnie zbieraj
            if isinstance(x, (list, tuple)):
                for e in x:
                    collect(e)
            else:
                # oczekujemy obiektu Tile
                vals.append((x.number, str(x.color)))
        collect(tile_seq)
        return tuple(vals)