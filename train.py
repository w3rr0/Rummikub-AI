import argparse

from environment import RummikubEnv

parser = argparse.ArgumentParser()
parser.add_argument("--players", type=int, default=2)
parser.add_argument("--blocks_start", type=int, default=14)
parser.add_argument("--blocks_range", type=int, default=13)

args = parser.parse_args()

if __name__ == "__main__":
    env = RummikubEnv(players=args.players, blocks_start=args.blocks_start, blocks_range=args.blocks_range)
    obs, _ = env.reset()
    done = False

    n_round = 0
    while not done:
        if env.engine.state.current_player == 0:
            n_round += 1
            print(f"\n------ Round {n_round} ------")
            env.render()

        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
