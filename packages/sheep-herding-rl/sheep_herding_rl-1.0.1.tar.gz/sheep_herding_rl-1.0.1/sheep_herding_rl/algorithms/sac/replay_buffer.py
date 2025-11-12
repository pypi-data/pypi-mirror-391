"""Replay buffer implementation for SAC."""

from __future__ import annotations

import numpy as np
import torch


class ReplayBuffer:
    """Fixed-size circular buffer storing transitions for SAC training."""
    
    def __init__(self, capacity: int, observation_shape, pen_vec_dim=2, action_dim=2, device='cpu'):
        self.capacity = capacity
        self.device = device

        self.obs_buf = np.zeros((capacity, *observation_shape), dtype=np.float32)
        self.pen_buf = np.zeros((capacity, pen_vec_dim), dtype=np.float32)
        self.act_buf = np.zeros((capacity, action_dim), dtype=np.float32)
        self.rew_buf = np.zeros((capacity, 1), dtype=np.float32)
        self.next_obs_buf = np.zeros((capacity, *observation_shape), dtype=np.float32)
        self.next_pen_buf = np.zeros((capacity, pen_vec_dim), dtype=np.float32)
        self.done_buf = np.zeros((capacity, 1), dtype=np.float32)

        self.ptr = 0
        self.size = 0

    def add(self, obs, pen, act, rew, next_obs, next_pen, done):
        self.obs_buf[self.ptr] = obs
        self.pen_buf[self.ptr] = pen
        self.act_buf[self.ptr] = act
        self.rew_buf[self.ptr] = rew
        self.next_obs_buf[self.ptr] = next_obs
        self.next_pen_buf[self.ptr] = next_pen
        self.done_buf[self.ptr] = float(done)

        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int):
        idxs = np.random.randint(0, self.size, size=batch_size)
        obs = torch.as_tensor(self.obs_buf[idxs], device=self.device)
        pen = torch.as_tensor(self.pen_buf[idxs], device=self.device)
        act = torch.as_tensor(self.act_buf[idxs], device=self.device)
        rew = torch.as_tensor(self.rew_buf[idxs], device=self.device)
        next_obs = torch.as_tensor(self.next_obs_buf[idxs], device=self.device)
        next_pen = torch.as_tensor(self.next_pen_buf[idxs], device=self.device)
        done = torch.as_tensor(self.done_buf[idxs], device=self.device)
        return obs, pen, act, rew, next_obs, next_pen, done
