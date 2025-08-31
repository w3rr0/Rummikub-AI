import argparse
from stable_baselines3 import PPO

from environment import RummikubEnv

parser = argparse.ArgumentParser()
parser.add_argument("--players", type=int, default=2)
parser.add_argument("--blocks_start", type=int, default=14)
parser.add_argument("--blocks_range", type=int, default=13)
parser.add_argument("--mode", type=str, default="test", choices=["test", "train"])
parser.add_argument("--total_games", type=int, default=1)
parser.add_argument("--model_path", type=str, default=None)
parser.add_argument("--save_path", type=str, default="models/ppo_rummikub")

args = parser.parse_args()

def play_game(env, model=None, render=False):
    obs, _ = env.reset()
    done = False
    n_round = 1
    moves_played = [0] * env.players
    tiles_played = [0] * env.players

    print(f"\n------ Round {n_round} ------")
    env.render()

    while not done:
        player = env.engine.state.current_player

        if model:
            action, _ = model.predict(obs, deterministic=True)
        else:
            action = env.action_space.sample()

        obs, reward, terminated, truncated, info = env.step(action)

        # Statistics
        if action < len(env.engine.enumerate_moves(player)):
            _, used_tiles = env.engine.enumerate_moves(player)[action]
            moves_played[player] += 1
            tiles_played[player] += len(used_tiles)

        if render:
            if player == env.players - 1:
                n_round += 1
                print(f"\n------ Round {n_round} ------")
            env.render()

        done = terminated or truncated

    winner = env.engine.state.winner
    return n_round, winner, moves_played, tiles_played


if __name__ == "__main__":
    env = RummikubEnv(players=args.players, blocks_start=args.blocks_start, blocks_range=args.blocks_range)

    model = None
    if args.model_path:
        model = PPO.load(args.model_path, env=env)
        print(f"Loaded model from {args.model_path}")

    if args.mode == "test":
        print(f"=== Test {args.total_games} {'game' if args.total_games == 1 else 'games'} ===")
        n_round, winner, moves_played, blocks_played = play_game(env, model=model, render=True)
        print("\n===== Game finished =====")
        print(f"Rounds played: {n_round}")
        for i in range(args.players):
            print(f"Player {i} - moves: {moves_played[i]}, blocks played: {blocks_played[i]}")
        print(f"Winner: Player {winner}")

    elif args.mode == "train":
        print(f"=== Training {args.total_games} {'games' if args.total_games != 1 else 'game'} ===")
        if not model:
            model = PPO("MlpPolicy", env, verbose=1)

        total_timesteps = args.total_games * 50
        model.learn(total_timesteps=total_timesteps)

        model.save(args.save_path)
        print(f"Model saved to {args.save_path}.zip")