# Usage Examples

## Basic Usage

### Creating a Simulator

```python
from sheep_herding_rl import Simulator
import sheep_herding_rl.config as config

# Create simulator with default settings
sim = Simulator()

# Run simulation loop
for step in range(1000):
    # Get observations
    dog_obs = sim.get_dog_observation()
    wolf_obs = sim.get_wolf_observation()
    
    # Your agent logic here
    dog_action = [0.5, 0.0]  # [forward_speed, turn_rate]
    wolf_action = [0.3, 0.1]
    
    # Step the simulation
    sim.step(dog_action, wolf_action)
    
    # Get rewards
    dog_reward = sim.get_dog_reward()
    wolf_reward = sim.get_wolf_reward()
    
    # Render (if display is enabled)
    sim.render()
```

## Training Agents

### Training with PPO

```python
from sheep_herding_rl import Simulator, PPOAgent
from sheep_herding_rl.trainers import OnPolicyTrainer
import torch

# Configuration
obs_dim = (config.OBSERVATION_CHANNELS, config.OBSERVATION_GRID_SIZE, config.OBSERVATION_GRID_SIZE)
action_dim = 2
metadata_dim = config.METADATA_DIM

# Create agent
agent = PPOAgent(obs_dim, action_dim, metadata_dim)

# Create simulator
sim = Simulator()

# Create trainer
trainer = OnPolicyTrainer(agent, sim)

# Train
trainer.train(
    num_episodes=1000,
    max_steps_per_episode=500,
    save_frequency=100
)
```

### Training with SAC

```python
from sheep_herding_rl import Simulator, SACAgent
from sheep_herding_rl.trainers import OffPolicyTrainer

# Create agent
agent = SACAgent(obs_dim, action_dim, metadata_dim)

# Create simulator
sim = Simulator()

# Create trainer
trainer = OffPolicyTrainer(agent, sim)

# Train
trainer.train(
    num_episodes=1000,
    batch_size=256,
    buffer_size=1000000
)
```

### Training with TD3

```python
from sheep_herding_rl import Simulator, TD3Agent
from sheep_herding_rl.trainers import OffPolicyTrainer

# Create agent
agent = TD3Agent(obs_dim, action_dim, metadata_dim)

# Create simulator  
sim = Simulator()

# Create trainer
trainer = OffPolicyTrainer(agent, sim)

# Train
trainer.train(
    num_episodes=1000,
    exploration_noise=0.1,
    policy_delay=2
)
```

## Custom Configuration

### Modifying Observation Settings

```python
import sheep_herding_rl.config as config

# Change to global observation mode
config.USE_GLOBAL_STATE_OBSERVATION = True

# Adjust observation grid size
config.OBSERVATION_GRID_SIZE = 32

# Change observation range (for local mode)
config.OBSERVATION_RANGE = 400

# Enable debug visualizations
config.DEBUG_SHOW_OBSERVATIONS = True
config.DEBUG_SHOW_PEN_DIRECTION = True
```

### Creating Custom Agents

```python
from sheep_herding_rl.agents import BaseAgent
import torch
import torch.nn as nn

class CustomAgent(BaseAgent):
    def __init__(self, obs_dim, action_dim, metadata_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Flatten(),
            nn.Linear(obs_dim[0] * obs_dim[1] * obs_dim[2] + metadata_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )
    
    def select_action(self, observation, metadata):
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(observation).unsqueeze(0)
            meta_tensor = torch.FloatTensor(metadata).unsqueeze(0)
            combined = torch.cat([obs_tensor.flatten(1), meta_tensor], dim=1)
            action = self.network(combined)
        return action.numpy()[0]
    
    def update(self, batch):
        # Implement your update logic
        pass
```

## Evaluation

### Evaluating a Trained Agent

```python
from sheep_herding_rl import Simulator
import torch

# Load trained agent
agent = torch.load('trained_agent.pth')
agent.eval()

# Create simulator
sim = Simulator()

# Evaluation loop
total_reward = 0
num_episodes = 100

for episode in range(num_episodes):
    sim.reset()
    episode_reward = 0
    done = False
    
    while not done:
        # Get observation
        obs = sim.get_dog_observation()
        
        # Select action
        action = agent.select_action(obs)
        
        # Step
        sim.step(action, wolf_action=[0, 0])
        reward = sim.get_dog_reward()
        episode_reward += reward
        
        # Check if done
        done = sim.is_done()
    
    total_reward += episode_reward
    print(f"Episode {episode}: Reward = {episode_reward}")

print(f"Average Reward: {total_reward / num_episodes}")
```

## Advanced Usage

### Multi-Agent Scenarios

```python
from sheep_herding_rl import Simulator

sim = Simulator()

# Train both dog and wolf simultaneously
for step in range(1000):
    dog_obs = sim.get_dog_observation()
    wolf_obs = sim.get_wolf_observation()
    
    # Both agents select actions
    dog_action = dog_agent.select_action(dog_obs)
    wolf_action = wolf_agent.select_action(wolf_obs)
    
    # Step simulation
    sim.step(dog_action, wolf_action)
    
    # Update both agents
    dog_reward = sim.get_dog_reward()
    wolf_reward = sim.get_wolf_reward()
    
    dog_agent.update(dog_obs, dog_action, dog_reward)
    wolf_agent.update(wolf_obs, wolf_action, wolf_reward)
```

### Logging and Visualization

```python
import matplotlib.pyplot as plt
from sheep_herding_rl import Simulator

sim = Simulator()
rewards = []

for episode in range(100):
    sim.reset()
    episode_reward = 0
    
    for step in range(500):
        obs = sim.get_dog_observation()
        action = agent.select_action(obs)
        sim.step(action, [0, 0])
        reward = sim.get_dog_reward()
        episode_reward += reward
    
    rewards.append(episode_reward)
    
    if episode % 10 == 0:
        print(f"Episode {episode}: Reward = {episode_reward}")

# Plot results
plt.plot(rewards)
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Training Progress')
plt.savefig('training_progress.png')
plt.show()
```

## Tips and Best Practices

1. **Start with smaller observation grids** for faster training
2. **Use global observations** for initial experiments
3. **Enable debug visualizations** to understand agent behavior
4. **Save models frequently** during training
5. **Use GPU** for faster neural network training
6. **Normalize observations** for better training stability
7. **Tune hyperparameters** based on your specific scenario
