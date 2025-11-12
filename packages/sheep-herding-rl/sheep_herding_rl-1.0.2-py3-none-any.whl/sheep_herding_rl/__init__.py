"""
Sheep Herding RL Package

A reinforcement learning environment for sheep herding simulation with PPO, SAC, and TD3 algorithms.
"""

__version__ = '1.0.2'
__author__ = 'ferip'
__email__ = ''

# Import main components
from .simulator import Simulator, SimulationState
from .actions import DogAction, WolfAction
from . import config

# Import agents
from .agents.base_agent import BaseAgent, RandomAgent

# Import algorithms
from .algorithms.ppo.agent import PPOAgent, PPOAgentConfig
from .algorithms.sac.agent import SACAgent, SACAgentConfig
from .algorithms.td3.agent import TD3Agent, TD3AgentConfig

# Import trainers
from .trainers.on_policy_trainer import OnPolicyTrainer, EpisodeLog as OnPolicyEpisodeLog
from .trainers.off_policy_trainer import OffPolicyTrainer, EpisodeLog as OffPolicyEpisodeLog
# Alias for convenience (both are identical)
EpisodeLog = OnPolicyEpisodeLog

# Import simulation components
from .sim.environment import Environment
from .sim.dog import Dog
from .sim.wolf import Wolf
from .sim.sheep import Sheep

__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Main components
    'Simulator',
    'SimulationState',
    'config',
    
    # Actions
    'DogAction',
    'WolfAction',
    
    # Agents
    'BaseAgent',
    'RandomAgent',
    'PPOAgent',
    'PPOAgentConfig',
    'SACAgent',
    'SACAgentConfig',
    'TD3Agent',
    'TD3AgentConfig',
    
    # Trainers
    'OnPolicyTrainer',
    'OffPolicyTrainer',
    'EpisodeLog',
    
    # Simulation
    'Environment',
    'Dog',
    'Wolf',
    'Sheep',
]
