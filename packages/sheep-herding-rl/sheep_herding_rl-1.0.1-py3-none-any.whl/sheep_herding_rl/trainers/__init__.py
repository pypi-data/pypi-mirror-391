"""Trainers for different algorithm types."""

from .off_policy_trainer import OffPolicyTrainer, EpisodeLog
from .on_policy_trainer import OnPolicyTrainer

__all__ = [
    "OffPolicyTrainer",
    "OnPolicyTrainer", 
    "EpisodeLog",
]
