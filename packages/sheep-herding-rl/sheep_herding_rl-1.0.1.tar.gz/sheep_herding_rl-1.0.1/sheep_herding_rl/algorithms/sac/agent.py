"""SAC agent implementation compatible with the project BaseAgent interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence, Type

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from ...actions import DogAction
from ...agents.base_agent import BaseAgent
from .replay_buffer import ReplayBuffer


@dataclass
class SACAgentConfig:
    observation_shape: Sequence[int]
    actor_class: Type[nn.Module]
    critic_class: Type[nn.Module]
    metadata_dim: int = 2  # Size of metadata vector (2 for local, 6 for global)
    action_dim: int = 2
    actor_lr: float = 3e-4
    critic_lr: float = 3e-4
    alpha_lr: float = 3e-4  # Temperature parameter learning rate
    gamma: float = 0.99
    tau: float = 0.005
    batch_size: int = 128
    replay_capacity: int = 200_000
    warmup_steps: int = 10_000
    steps_per_update: int = 1  # Do 1 update every N environment steps
    max_updates_per_step: int = 1  # Max SGD updates per trigger (when update is triggered)
    target_entropy: float | None = None  # Defaults to -action_dim if None
    automatic_entropy_tuning: bool = True
    use_amp: bool = False  # Mixed precision training (CUDA only)
    device: str = "cpu"


class SACAgent(BaseAgent):
    """SAC agent with automatic entropy tuning and stochastic policy."""

    def __init__(
        self,
        config: SACAgentConfig,
        action_cls: Type[DogAction] = DogAction,
    ) -> None:
        self.config = config
        self.device = torch.device(config.device)
        self.action_dim = config.action_dim
        self.action_cls = action_cls

        # Instantiate stochastic actor
        self.actor = config.actor_class(
            observation_shape=config.observation_shape,
            metadata_dim=config.metadata_dim,
            action_dim=config.action_dim,
        ).to(self.device)

        # Instantiate twin critics
        self.critic = config.critic_class(
            observation_shape=config.observation_shape,
            metadata_dim=config.metadata_dim,
            action_dim=config.action_dim,
        ).to(self.device)
        
        # Target critic (no target actor in SAC)
        self.critic_target = config.critic_class(
            observation_shape=config.observation_shape,
            metadata_dim=config.metadata_dim,
            action_dim=config.action_dim,
        ).to(self.device)
        self.critic_target.load_state_dict(self.critic.state_dict())

        # Optimizers
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=config.actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=config.critic_lr)

        # Automatic entropy tuning
        self.automatic_entropy_tuning = config.automatic_entropy_tuning
        # Default target_entropy to -action_dim if not provided
        self.target_entropy = config.target_entropy if config.target_entropy is not None else -float(config.action_dim)
        
        if self.automatic_entropy_tuning:
            self.log_alpha = nn.Parameter(torch.zeros(1, device=self.device))
            self.alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=config.alpha_lr)
        else:
            # Fixed alpha
            self.log_alpha = torch.tensor(np.log(0.2), device=self.device, requires_grad=False)
            self.alpha_optimizer = None

        # Mixed precision (AMP) - only on CUDA
        self.use_amp = config.use_amp and (self.device.type == 'cuda')
        if self.use_amp:
            torch.backends.cudnn.benchmark = True  # Fixed input sizes, faster convs
            self.critic_scaler = torch.amp.GradScaler('cuda')
            self.actor_scaler = torch.amp.GradScaler('cuda')
        else:
            self.critic_scaler = None
            self.actor_scaler = None

        # Replay buffer
        self.replay_buffer = ReplayBuffer(
            capacity=config.replay_capacity,
            observation_shape=tuple(config.observation_shape),
            pen_vec_dim=config.metadata_dim,
            action_dim=config.action_dim,
            device=str(self.device),
        )

        self.total_steps = 0
        self.update_step = 0
        self.training_mode = True

    @property
    def alpha(self):
        """Temperature parameter (controls exploration vs exploitation)."""
        return self.log_alpha.exp()

    # ------------------------------------------------------------------
    # BaseAgent API
    # ------------------------------------------------------------------
    def act(self, observation: np.ndarray, metadata_vector: np.ndarray):
        obs_np = np.asarray(observation, dtype=np.float32)
        metadata_np = np.asarray(metadata_vector, dtype=np.float32)
        observation_tensor = torch.from_numpy(obs_np).unsqueeze(0).to(self.device)
        metadata_tensor = torch.from_numpy(metadata_np).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if self.training_mode:
                # Sample stochastic action during training
                action, _, _ = self.actor.sample(observation_tensor, metadata_tensor)
            else:
                # Use mean action during evaluation
                _, _, action = self.actor.sample(observation_tensor, metadata_tensor)
        
        action_np = action.squeeze(0).cpu().numpy()

        # Convert from [-1, 1] to environment action space
        env_action_vector = self._normalized_to_env_action(action_np)
        return self.action_cls.from_vector(env_action_vector)

    def observe(
        self,
        observation: np.ndarray,
        metadata_vector: np.ndarray,
        action,
        reward: float,
        next_observation: np.ndarray,
        next_metadata_vector: np.ndarray,
        done: bool,
        info: dict,
    ) -> None:
        action_vector = action.to_vector()
        normalized_action = self._env_to_normalized_action(action_vector)

        self.replay_buffer.add(
            observation,
            metadata_vector,
            normalized_action,
            reward,
            next_observation,
            next_metadata_vector,
            done,
        )

        self.total_steps += 1
        if self.total_steps < self.config.warmup_steps:
            return

        if self.replay_buffer.size < self.config.batch_size:
            return

        # Update only every N steps (decouples SGD frequency from env FPS)
        if self.total_steps % self.config.steps_per_update == 0:
            for _ in range(self.config.max_updates_per_step):
                self._update()

    def episode_start(self):
        pass

    def episode_end(self, total_reward: float):
        pass

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save(self, path: str, include_replay: bool = False, max_replay_items: int = 0) -> None:
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        
        payload = {
            "config": asdict(self.config),
            "actor": self.actor.state_dict(),
            "critic": self.critic.state_dict(),
            "critic_target": self.critic_target.state_dict(),
            "actor_opt": self.actor_optimizer.state_dict(),
            "critic_opt": self.critic_optimizer.state_dict(),
            "log_alpha": self.log_alpha.detach().cpu(),
            "alpha_opt": self.alpha_optimizer.state_dict() if self.alpha_optimizer is not None else None,
            "critic_scaler": self.critic_scaler.state_dict() if self.critic_scaler is not None else None,
            "actor_scaler": self.actor_scaler.state_dict() if self.actor_scaler is not None else None,
            "total_steps": self.total_steps,
            "update_step": self.update_step,
        }
        
        if include_replay:
            N = self.replay_buffer.size
            if max_replay_items > 0:
                N = min(N, max_replay_items)
            start = (self.replay_buffer.ptr - N) % self.replay_buffer.capacity
            if N == 0:
                rb = None
            else:
                idxs = (np.arange(N) + start) % self.replay_buffer.capacity
                rb = {
                    "capacity": self.replay_buffer.capacity,
                    "size": int(N),
                    "ptr": int(N % self.replay_buffer.capacity),
                    "obs": self.replay_buffer.obs_buf[idxs],
                    "pen": self.replay_buffer.pen_buf[idxs],
                    "act": self.replay_buffer.act_buf[idxs],
                    "rew": self.replay_buffer.rew_buf[idxs],
                    "next_obs": self.replay_buffer.next_obs_buf[idxs],
                    "next_pen": self.replay_buffer.next_pen_buf[idxs],
                    "done": self.replay_buffer.done_buf[idxs],
                }
            payload["replay"] = rb
        
        torch.save(payload, path)

    def load(self, path: str, map_location: str | torch.device | None = None, strict: bool = True) -> None:
        if map_location is None:
            map_location = self.device

        checkpoint = torch.load(path, map_location=map_location, weights_only=False)
        
        if "actor" in checkpoint:
            self.actor.load_state_dict(checkpoint["actor"], strict=strict)
        if "critic" in checkpoint:
            self.critic.load_state_dict(checkpoint["critic"], strict=strict)

        if "critic_target" in checkpoint and checkpoint["critic_target"] is not None:
            self.critic_target.load_state_dict(checkpoint["critic_target"], strict=strict)
        else:
            self.critic_target.load_state_dict(self.critic.state_dict())

        if "actor_opt" in checkpoint and checkpoint["actor_opt"] is not None:
            self.actor_optimizer.load_state_dict(checkpoint["actor_opt"])
            # Move optimizer state tensors to the correct device
            for state in self.actor_optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.to(self.device)

        if "critic_opt" in checkpoint and checkpoint["critic_opt"] is not None:
            self.critic_optimizer.load_state_dict(checkpoint["critic_opt"])
            for state in self.critic_optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.to(self.device)

        if "log_alpha" in checkpoint and checkpoint["log_alpha"] is not None:
            with torch.no_grad():
                self.log_alpha.data.copy_(checkpoint["log_alpha"].to(self.device).reshape_as(self.log_alpha.data))
        if "alpha_opt" in checkpoint and checkpoint["alpha_opt"] is not None and self.alpha_optimizer is not None:
            self.alpha_optimizer.load_state_dict(checkpoint["alpha_opt"])
            for state in self.alpha_optimizer.state.values():
                for k, v in state.items():
                    if isinstance(v, torch.Tensor):
                        state[k] = v.to(self.device)

        if self.critic_scaler is not None and checkpoint.get("critic_scaler"):
            try:
                self.critic_scaler.load_state_dict(checkpoint["critic_scaler"])
            except Exception:
                pass
        if self.actor_scaler is not None and checkpoint.get("actor_scaler"):
            try:
                self.actor_scaler.load_state_dict(checkpoint["actor_scaler"])
            except Exception:
                pass

        replay_data = checkpoint.get("replay")
        if replay_data is not None:
            self._load_replay(replay_data)
        self.total_steps = checkpoint.get("total_steps", 0)
        self.update_step = checkpoint.get("update_step", 0)
        
        self.actor.train()
        self.critic.train()
        self.critic_target.eval()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def set_eval_mode(self, eval_mode: bool) -> None:
        self.training_mode = not eval_mode
        if eval_mode:
            self.actor.eval()
            self.critic.eval()
        else:
            self.actor.train()
            self.critic.train()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _update(self) -> None:
        obs, pen, act, rew, next_obs, next_pen, done = self.replay_buffer.sample(self.config.batch_size)

        # ----- Critic update (with AMP when CUDA) -----
        with torch.amp.autocast('cuda', enabled=self.use_amp), torch.no_grad():
            # Sample next actions from current policy
            next_actions, next_log_probs, _ = self.actor.sample(next_obs, next_pen)
            
            # Compute target Q-values
            q1_target, q2_target = self.critic_target(next_obs, next_pen, next_actions)
            q_target = torch.min(q1_target, q2_target)
            
            # V(s') = Q(s', a') - α * log π(a'|s')
            v_target = q_target - self.alpha * next_log_probs
            
            # Bellman backup
            backup = rew + self.config.gamma * (1.0 - done) * v_target

        self.critic_optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast('cuda', enabled=self.use_amp):
            # Current Q estimates
            q1_current, q2_current = self.critic(obs, pen, act)
            
            # MSE loss for both critics
            critic_loss = F.mse_loss(q1_current, backup) + F.mse_loss(q2_current, backup)

        if self.critic_scaler is not None:
            self.critic_scaler.scale(critic_loss).backward()
            self.critic_scaler.unscale_(self.critic_optimizer)
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 1.0)
            self.critic_scaler.step(self.critic_optimizer)
            self.critic_scaler.update()
        else:
            critic_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 1.0)
            self.critic_optimizer.step()

        # ----- Actor update (with AMP) -----
        self.actor_optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast('cuda', enabled=self.use_amp):
            # Sample actions from current policy
            sampled_actions, log_probs, _ = self.actor.sample(obs, pen)
            
            # Compute Q-values for sampled actions
            q1_pi, q2_pi = self.critic(obs, pen, sampled_actions)
            q_pi = torch.min(q1_pi, q2_pi)
            
            # Actor loss: maximize Q - α * log π (minimize negative)
            actor_loss = (self.alpha * log_probs - q_pi).mean()

        if self.actor_scaler is not None:
            self.actor_scaler.scale(actor_loss).backward()
            self.actor_scaler.unscale_(self.actor_optimizer)
            torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 1.0)
            self.actor_scaler.step(self.actor_optimizer)
            self.actor_scaler.update()
        else:
            actor_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 1.0)
            self.actor_optimizer.step()

        # ----- Temperature (alpha) update -----
        if self.automatic_entropy_tuning:
            # Temperature loss: α * (log π + target_entropy)
            alpha_loss = -(self.log_alpha * (log_probs + self.target_entropy).detach()).mean()
            
            self.alpha_optimizer.zero_grad(set_to_none=True)
            alpha_loss.backward()
            self.alpha_optimizer.step()

        # ----- Target network soft update -----
        self._soft_update(self.critic, self.critic_target)

        self.update_step += 1

    def _soft_update(self, online: nn.Module, target: nn.Module) -> None:
        for target_param, param in zip(target.parameters(), online.parameters()):
            target_param.data.copy_(
                target_param.data * (1.0 - self.config.tau) + param.data * self.config.tau
            )

    def _env_to_normalized_action(self, action_vector: np.ndarray) -> np.ndarray:
        """Convert environment action [0,1], [-1,1] to network output [-1,1], [-1,1]."""
        normalized_forward = np.clip(action_vector[0], 0.0, 1.0) * 2.0 - 1.0
        normalized_turn = np.clip(action_vector[1], -1.0, 1.0)
        return np.array([normalized_forward, normalized_turn], dtype=np.float32)

    def _normalized_to_env_action(self, normalized_action: np.ndarray) -> np.ndarray:
        """Convert network output [-1,1], [-1,1] to environment action [0,1], [-1,1]."""
        forward = np.clip((normalized_action[0] + 1.0) * 0.5, 0.0, 1.0)
        turn = np.clip(normalized_action[1], -1.0, 1.0)
        return np.array([forward, turn], dtype=np.float32)

    def _load_replay(self, replay_data: dict) -> None:
        obs = replay_data.get("obs")
        pen = replay_data.get("pen")
        actions = replay_data.get("act")
        rewards = replay_data.get("rew")
        next_obs = replay_data.get("next_obs")
        next_pen = replay_data.get("next_pen")
        dones = replay_data.get("done")

        if obs is None:
            return

        cap = int(replay_data["capacity"])
        if cap == self.replay_buffer.capacity and obs.shape[1:] == self.replay_buffer.obs_buf.shape[1:]:
            N = int(replay_data["size"])
            self.replay_buffer.size = N
            self.replay_buffer.ptr = int(replay_data["ptr"])
            self.replay_buffer.obs_buf[:N] = obs
            self.replay_buffer.pen_buf[:N] = pen
            self.replay_buffer.act_buf[:N] = actions
            self.replay_buffer.rew_buf[:N] = rewards
            self.replay_buffer.next_obs_buf[:N] = next_obs
            self.replay_buffer.next_pen_buf[:N] = next_pen
            self.replay_buffer.done_buf[:N] = dones

    def train(self) -> None:  # pragma: no cover - convenience alias
        self.set_eval_mode(False)

    def eval(self) -> None:  # pragma: no cover - convenience alias
        self.set_eval_mode(True)
