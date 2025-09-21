from stable_baselines3.common.vec_env import SubprocVecEnv
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
import argparse
import numpy as np
import time
import torch

from python.environment import RummikubEnv

parser = argparse.ArgumentParser()

parser.add_argument("--players", type=int, default=2)
parser.add_argument("--blocks_start", type=int, default=14)
parser.add_argument("--blocks_range", type=int, default=13)
parser.add_argument("--mode", type=str, default="test", choices=["test", "train", "play"])
parser.add_argument("--total_games", type=int, default=1)
parser.add_argument("--model_path", type=str, default=None)
parser.add_argument("--save_path", type=str, default="models/ppo_rummikub")
parser.add_argument("--engine", type=str, choices=["cpp", "python"], default="cpp")
parser.add_argument("--num_envs", type=int, default=4)
parser.add_argument("--n_steps", type=int, default=128)
parser.add_argument("--device", type=str, choices=["cpu", "cuda", "mps", "auto"], default="cpu")

args = parser.parse_args()

def mask_fn(env):
    return env._get_mask()

def play_game(env, model=None, render=False):
    obs, info = env.reset()
    done = False
    n_round = 1
    moves_played = [0] * env.players
    tiles_played = [0] * env.players

    print(f"\n------ Round {n_round} ------")
    env.render()

    while not done:
        player = env.engine.state.current_player

        mask = info["action_mask"]
        if model:
            action, _ = model.predict(obs, action_masks=mask, deterministic=True)
        else:
            valid_actions = np.where(mask)[0]
            action = np.random.choice(valid_actions)


        obs, reward, terminated, truncated, info = env.step(action)

        # Statistics
        if 1 < action < env.max_actions:
            used_tiles = env.actions[action - 2]
            #_, used_tiles = env.engine.enumerate_moves(player)[action]
        else:
            used_tiles = []
        moves_played[player] += 1
        tiles_played[player] += len(used_tiles)

        if render:
            if player == env.players - 1 and int(action) in {0, 1}:
                n_round += 1
                print(f"\n------ Round {n_round} ------")
            env.render()

        done = terminated or truncated

    winner = env.engine.state.winner
    return n_round, winner, moves_played, tiles_played


if __name__ == "__main__":
    if args.device == "auto":
        if torch.cuda.is_available():
           device = "cuda"
        elif torch.backends.mps.is_available():
           device = "mps"
        else:
           device = "cpu"
    else:
        device = args.device
    model = None


    def load_model() -> None:
        global model
        if args.model_path:
            model = MaskablePPO.load(args.model_path, env=env, device=device)
            print(f"Loaded model from {args.model_path}")

    if args.mode == "test":
        env = RummikubEnv(players=args.players, blocks_start=args.blocks_start, blocks_range=args.blocks_range, version=args.engine)
        load_model()

        print(f"=== Test {args.total_games} {'game' if args.total_games == 1 else 'games'} on {torch.cuda.get_device_name(0) if device == "cuda" else device} ===")
        nr, w, mp, bp, t = 0, [0] * args.players, [0] * args.players, [0] * args.players, [0] * args.total_games
        for j in range(args.total_games):
            start = time.time()
            n_round, winner, moves_played, blocks_played = play_game(env, model=model, render=True)
            end = time.time()
            t[j] = round(end - start, 2)
            nr += n_round
            w[winner] += 1
            for player in range(args.players):
                mp[player] += moves_played[player]
                bp[player] += blocks_played[player]

            print(f"\n===== Game {j+1} finished =====")
            print(f"Rounds played: {n_round}")
            for i in range(args.players):
                print(f"Player {i} - moves: {moves_played[i]}, tiles played: {blocks_played[i]}")
            print(f"Winner: Player {winner}")

        print(f"\n===== {args.total_games} games finished =====")
        print(f"Total rounds: {nr}")
        print(f"Average game time: {sum(t) / len(t)}")
        for i in range(args.players):
            print(f"Player {i} - Total wins: {w[i]}, Total moves: {mp[i]}, Total tiles placed: {bp[i]}")

    elif args.mode == "train":
        def make_env():
            return lambda: ActionMasker(RummikubEnv(players=args.players, blocks_start=args.blocks_start, blocks_range=args.blocks_range, version=args.engine, render_mask=False), mask_fn)

        env = SubprocVecEnv([make_env() for _ in range(args.num_envs)])
        load_model()

        print(f"=== Training for around {args.total_games} {'games' if args.total_games != 1 else 'game'} on {torch.cuda.get_device_name(0) if device == "cuda" else device} ===")
        if not model:
            model = MaskablePPO("MlpPolicy", n_steps=args.n_steps, env=env, verbose=2, device=device)

        total_timesteps = args.total_games * args.players * args.blocks_range**2
        model.learn(total_timesteps=total_timesteps)

        model.save(args.save_path)
        print(f"Model saved to {args.save_path}.zip")

    elif args.mode == "play":
        env = RummikubEnv(players=args.players, blocks_start=args.blocks_start, blocks_range=args.blocks_range, version=args.engine)
        load_model()

        obs, info = env.reset()
        done = False
        n_round = 1

        print(f"\n=== Human vs AI Game ===")
        print(f"\n------ Round {n_round} ------")
        env.render()

        while not done:
            player = env.engine.state.current_player
            mask = info["action_mask"]

            if player == 0:
                print("\nYour hand:", env.engine.state.hands[player])
                print("Possible actions:", np.where(mask)[0])
                action = int(input("Chose actions number: "))
                while not mask[action]:
                    action = int(input("Incorrect action, chose again: "))
            else:
                if model:
                    action, _ = model.predict(obs, action_mask=mask, deterministic=True)
                else:
                    valid_actions = np.where(mask)[0]
                    action = np.random.choice(valid_actions)

            obs, reward, terminated, truncated, info = env.step(action)

            if player == env.players - 1 and action in {0, 1}:
                n_round += 1
                print(f"\n------ Round {n_round} ------")

            env.render()
            done = terminated or truncated

        winner = env.engine.state.winner
        print(f"\n===== Game end =====")
        print(f"Winner: {'You' if winner == 0 else f'AI (Player {winner})'}")