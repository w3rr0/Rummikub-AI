# Rummikub-AI
> A program for training an AI model to play Rummikub and its various versions.

## Table of Contents
* [Goal to achieve](#goal-to-achieve)
* [Core technologies](#core-technologies)
* [Features](#features)
* [Setup](#setup)
* [Usage](#usage)
* [Room for Improvement](#room-for-improvement)
* [License](#license)
* [Contact](#contact)


## Goal to achieve
The goal of the project is to train a model that makes the best possible decisions in Rummikub.
It's impossible to win 100% of games because, unlike chess or Go,
there's a certain randomness that prevents it from winning every time.
However, the model should win more than half of the games against a human player over a larger number of games.


## Core technologies
- languages:
    - Python - version 3.12
    - C++ - version 17
- model:
  - MaskablePPO
- environment:
  - gymnasium
  - SubprocVecEnv


## Features
- Learning new models
- Training existing models
- Testing trained models and game engines
- Playing against a trained model


## Setup

#### Clone repo

```sh
    git clone https://github.com/w3rr0/Rummikub-AI
```

#### Create and activate virtual env

- Linux/MacOS

```sh
    python -m venv .venv
    source .venv/bin/activate
```

- Winrows (PowerShell)

```sh
    python -m venv .venv
    .venv\Scripts\Activate.ps1
```

#### Install requirements

```sh
    pip install -r requirements.txt
```

#### Compile C++ code

```sh
    pip install -e .
```


## Usage
To get started, run the train.py file with the selected flags:
- --mode {test}
  - test (test game between AI)
  - train (training a new or existing model)
  - play (game between human and AI)
- --players (number of players to participate in the game) {2}
- --blocks_range (the value of the highest block in the pool) {13}
- --blocks_start (the number of blocks awarded to each player at the start) {14}
- --total_games (number of games to be played) {1}
- --engine {cpp}
  - python (obsolete, not recommended for use)
  - cpp (performance engine written in c++)
- --num_envs (number of parallel environments, works only in train mode) {4}
- --n_steps (number of steps collected per environment before each PPO update) {512}
- --device {cpu}
  - auto (automatically selects the device by checking what is available, GPU takes priority)
  - cpu (default cpu, can be run on any device)
  - cuda (requires an nvidia GPU and cuda software installed)
  - mps (requires an Apple M series device)
- --model_path (path to the model to be used in gameplay) {None}
- --save_path (the path where the model will be saved after training) {models/ppo_rummikub}

<p align="right">{} - default values</p>

#### example of use

```sh
    python train.py --mode train --blocks_range 8 --blocks_start 9 --total_games 100 --save_path models/ppo_rummikub8.9
```


## Room for Improvement
Currently, the main bottleneck in the system is the masking mechanism,
which requires a large number of CPU computations.
This significantly slows down the overall performance.
Finding a faster algorithm or further optimizing the existing one could provide a noticeable speedup.
Additionally, finding a way to efficiently leverage GPU acceleration in this process would be highly beneficial.


## License
This project is open source and available under the [MIT License](LICENSE).


## Contact
Created by @w3rr0:
[konradmateja65@gmail.com](mailto:konradmateja65@gmail.com).
Feel free to contact me.
