# Sheep Herding RL

A reinforcement learning environment for sheep herding simulation with multiple agent implementations including PPO, SAC, and TD3 algorithms.

## Description

This package provides a pygame-based simulation environment where agents (dogs and wolves) interact with sheep in a herding scenario. The environment supports both local ego-centric and global observation modes, making it suitable for various reinforcement learning experiments.

## Features

- **Multi-Agent Environment**: Supports dog (herder) and wolf (predator) agents
- **Multiple RL Algorithms**: Implementations of PPO, SAC, and TD3
- **Flexible Observation Modes**: 
  - Local ego-centric grid observations
  - Global state observations
- **Configurable Parameters**: Easy-to-modify configuration system
- **Visualization**: Real-time rendering with debug modes
- **Training Framework**: Built-in trainers for on-policy and off-policy algorithms

## Installation

### From Source

```bash
git clone https://github.com/dzijo/ferit-hackathon.git
cd ferit-hackathon
pip install -e .
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

### Dependencies

- Python >= 3.8
- PyTorch >= 2.0.0
- pygame
- numpy
- pillow
- scipy
- pyyaml
- matplotlib

## Project Structure

```
sheep-herding-rl/
├── agents/              # Base agent classes
├── algorithms/          # RL algorithm implementations
│   ├── ppo/            # Proximal Policy Optimization
│   ├── sac/            # Soft Actor-Critic
│   └── td3/            # Twin Delayed DDPG
├── sim/                # Simulation environment
│   ├── environment.py  # Main environment class
│   ├── dog.py          # Dog agent
│   ├── wolf.py         # Wolf agent
│   └── sheep.py        # Sheep entities
├── trainers/           # Training utilities
├── utils/              # Helper utilities
├── config.py           # Configuration parameters
├── simulator.py        # Main simulator class
└── actions.py          # Action definitions
```

## Quick Start

```python
from sheep_herding_rl import Simulator
from sheep_herding_rl import config

# Create a simulator instance
sim = Simulator()

# Run a step
state = sim.get_state()
dog_obs = sim.get_dog_observation()
wolf_obs = sim.get_wolf_observation()

# Take actions
dog_action = [0.5, 0.0]  # [forward_speed, turn_rate]
wolf_action = [0.3, 0.1]
sim.step(dog_action, wolf_action)

# Get rewards
dog_reward = sim.get_dog_reward()
wolf_reward = sim.get_wolf_reward()
```

## Configuration

All simulation parameters can be modified in `config.py`:

- **Observation parameters**: Grid size, range, channels
- **Screen dimensions**: Width, height
- **Debug modes**: Visualization options
- **Splatting methods**: Gaussian, bilinear, or discrete

## Training

The package includes trainers for different algorithm types:

```python
from trainers.on_policy_trainer import OnPolicyTrainer
from algorithms.ppo.agent import PPOAgent

# Create and train an agent
agent = PPOAgent(obs_dim, action_dim)
trainer = OnPolicyTrainer(agent, sim)
trainer.train(num_episodes=1000)
```

## Algorithms

### PPO (Proximal Policy Optimization)
On-policy algorithm with clipped objective for stable training.

### SAC (Soft Actor-Critic)
Off-policy algorithm with entropy regularization for exploration.

### TD3 (Twin Delayed DDPG)
Off-policy algorithm with twin critics and delayed policy updates.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{sheep_herding_rl,
  title = {Sheep Herding RL: A Multi-Agent Reinforcement Learning Environment},
  author = {ferip},
  year = {2025},
  url = {https://github.com/dzijo/ferit-hackathon}
}
```

## Acknowledgments

Created for the FERIT Hackathon 2025.
