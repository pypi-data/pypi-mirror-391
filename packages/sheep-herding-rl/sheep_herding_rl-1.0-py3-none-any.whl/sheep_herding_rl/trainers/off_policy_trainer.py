"""Off-policy training loop for TD3, SAC, DDPG, and other off-policy algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import shutil
import time
from typing import Callable, List, Optional, Tuple
from .. import config
import pygame

from ..actions import WolfAction
from ..agents.base_agent import BaseAgent
from ..simulator import Simulator


@dataclass
class EpisodeLog:
    episode: int
    steps: int
    dog_reward: float
    wolf_reward: float
    sheep_in_pen: int
    sheep_remaining: int


class OffPolicyTrainer:
    """
    High-level trainer for off-policy RL algorithms (TD3, SAC, DDPG, DQN, etc.).
    
    Works with any agent that uses a replay buffer and step-by-step learning.
    """

    def __init__(
        self,
        simulator: Simulator,
        dog_agent: BaseAgent,
        wolf_agent: Optional[BaseAgent] = None,
        max_steps_per_episode: int = 2000,
        log_callback: Optional[Callable[[EpisodeLog], None]] = None,
        save_dir: Optional[str] = None,
        save_every_episodes: int = 10,
        training_script_path: Optional[str] = None,
    ) -> None:
        self.simulator = simulator
        self.dog_agent = dog_agent
        self.wolf_agent = wolf_agent
        self.max_steps = max_steps_per_episode
        self.log_callback = log_callback
        self.global_step = 0
        self.render_enabled = False
        self._allow_render_toggle = False
        self._render_stride = 1
        
        # Checkpoint saving
        self.save_dir = save_dir
        self.save_every_episodes = save_every_episodes
        self._checkpoint_dir: Optional[Path] = None
        self.training_script_path = training_script_path
        
        # Timing stats
        self.timing_stats = {
            'env_step_time': 0.0,
            'dog_act_time': 0.0,
            'wolf_act_time': 0.0,
            'dog_observe_time': 0.0,
            'wolf_observe_time': 0.0,
            'render_time': 0.0,
        }
        self.timing_counts = {key: 0 for key in self.timing_stats.keys()}
    
    def _create_checkpoint_dir(self) -> Path:
        """Create timestamped checkpoint directory."""
        if self._checkpoint_dir is not None:
            return self._checkpoint_dir
        
        if self.save_dir is None:
            raise ValueError("save_dir must be set to create checkpoints")
        
        # Create base save directory
        base_dir = Path(self.save_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        checkpoint_dir = base_dir / f"run_{timestamp}"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self._checkpoint_dir = checkpoint_dir
        
        # Save the training script for reproducibility
        if self.training_script_path is not None and os.path.exists(self.training_script_path):
            script_backup_path = checkpoint_dir / os.path.basename(self.training_script_path)
            shutil.copy2(self.training_script_path, script_backup_path)
            print(f"[trainer] Saved training script to: {script_backup_path}")
        
        print(f"[trainer] Checkpoints will be saved to: {checkpoint_dir}")
        return checkpoint_dir
    
    def save_checkpoint(self, episode: int) -> None:
        """Save agent checkpoints.
        
        Args:
            episode: Current episode number
        """
        if self.save_dir is None:
            return
        
        checkpoint_dir = self._create_checkpoint_dir()
        
        # Save dog agent (only if save is implemented)
        dog_checkpoint_path = checkpoint_dir / f"dog_ep{episode:04d}.pt"
        if hasattr(self.dog_agent, 'save'):
            try:
                self.dog_agent.save(str(dog_checkpoint_path))
            except NotImplementedError:
                pass  # Agent doesn't support saving, skip
        
        # Save wolf agent if trainable (only if save is implemented)
        if self.wolf_agent is not None and hasattr(self.wolf_agent, 'save'):
            wolf_checkpoint_path = checkpoint_dir / f"wolf_ep{episode:04d}.pt"
            try:
                self.wolf_agent.save(str(wolf_checkpoint_path))
            except NotImplementedError:
                pass  # Agent doesn't support saving, skip
        
        # Also save as "latest" for easy resumption
        dog_latest_path = checkpoint_dir / "dog_latest.pt"
        if hasattr(self.dog_agent, 'save'):
            try:
                self.dog_agent.save(str(dog_latest_path))
            except NotImplementedError:
                pass
        
        if self.wolf_agent is not None and hasattr(self.wolf_agent, 'save'):
            wolf_latest_path = checkpoint_dir / "wolf_latest.pt"
            try:
                self.wolf_agent.save(str(wolf_latest_path))
            except NotImplementedError:
                pass
        
        print(f"[trainer] Checkpoint saved at episode {episode}")
    
    def load_checkpoint(self, dog_path: str, wolf_path: Optional[str] = None) -> None:
        """Load agent checkpoints.
        
        Args:
            dog_path: Path to dog agent checkpoint
            wolf_path: Optional path to wolf agent checkpoint
        """
        if hasattr(self.dog_agent, 'load'):
            self.dog_agent.load(dog_path)
            print(f"[trainer] Loaded dog checkpoint from: {dog_path}")
        
        if wolf_path is not None and self.wolf_agent is not None and hasattr(self.wolf_agent, 'load'):
            self.wolf_agent.load(wolf_path)
            print(f"[trainer] Loaded wolf checkpoint from: {wolf_path}")

    def run(
        self,
        num_episodes: int,
        render_every_steps: int = 0,
        start_render_enabled: bool = False,
        allow_render_toggle: bool = False,
        log_interval: int = 1,
    ) -> List[EpisodeLog]:
        """Run training and optionally render frames every N simulator steps."""

        history: List[EpisodeLog] = []
        render_stride = render_every_steps if render_every_steps > 0 else 1
        self._allow_render_toggle = allow_render_toggle
        self.render_enabled = start_render_enabled and render_every_steps > 0
        self.global_step = 0
        self._render_stride = render_stride
        quit_requested = False

        for episode in range(num_episodes):
            self.dog_agent.episode_start()
            if self.wolf_agent is not None:
                self.wolf_agent.episode_start()

            (dog_obs, dog_pen), (wolf_obs, wolf_pen) = self.simulator.reset()
            dog_episode_reward = 0.0
            wolf_episode_reward = 0.0

            for step in range(self.max_steps):
                if self._allow_render_toggle and self._process_window_events():
                    quit_requested = True
                    break

                t0 = time.perf_counter()
                dog_action = self.dog_agent.act(dog_obs, dog_pen)
                t1 = time.perf_counter()
                self.timing_stats['dog_act_time'] += (t1 - t0)
                self.timing_counts['dog_act_time'] += 1

                if self.wolf_agent is not None:
                    t0 = time.perf_counter()
                    wolf_action = self.wolf_agent.act(wolf_obs, wolf_pen)
                    t1 = time.perf_counter()
                    self.timing_stats['wolf_act_time'] += (t1 - t0)
                    self.timing_counts['wolf_act_time'] += 1
                else:
                    wolf_action = WolfAction.zero()

                t0 = time.perf_counter()
                (
                    next_dog_obs,
                    next_dog_pen,
                    dog_reward,
                    next_wolf_obs,
                    next_wolf_pen,
                    wolf_reward,
                    info,
                ) = self.simulator.step(dog_action, wolf_action)
                t1 = time.perf_counter()
                self.timing_stats['env_step_time'] += (t1 - t0)
                self.timing_counts['env_step_time'] += 1

                t0 = time.perf_counter()
                self.dog_agent.observe(
                    dog_obs,
                    dog_pen,
                    dog_action,
                    dog_reward,
                    next_dog_obs,
                    next_dog_pen,
                    info.get("done", False),
                    info,
                )
                t1 = time.perf_counter()
                self.timing_stats['dog_observe_time'] += (t1 - t0)
                self.timing_counts['dog_observe_time'] += 1

                # Wolf transition storage logic:
                # - Store if wolf just got killed (learn to avoid death)
                # - Store if wolf just ate a sheep (learn to get reward)
                # - Store if wolf is alive and not in cooldown (normal learning)
                # - Skip if wolf is dead (already dead, can't act)
                # - Skip if wolf is in cooldown (can't act, forced inaction)
                if self.wolf_agent is not None:
                    wolf_just_killed = info.get('wolf_killed', False)
                    wolf_just_ate = info.get('wolf_just_ate', False)
                    wolf_is_dead = info.get('wolf_is_dead', False)
                    wolf_in_cooldown = info.get('wolf_in_cooldown', False)
                    
                    # Store transition if:
                    # 1. Wolf just got killed (important negative reward signal)
                    # 2. Wolf just ate a sheep (important positive reward signal)
                    # 3. Wolf is alive AND not in cooldown (can act normally)
                    should_store = wolf_just_killed or wolf_just_ate or (not wolf_is_dead and not wolf_in_cooldown)
                    
                    if should_store:
                        t0 = time.perf_counter()
                        self.wolf_agent.observe(
                            wolf_obs,
                            wolf_pen,
                            wolf_action,
                            wolf_reward,
                            next_wolf_obs,
                            next_wolf_pen,
                            info.get("done", False),
                            info,
                        )
                        t1 = time.perf_counter()
                        self.timing_stats['wolf_observe_time'] += (t1 - t0)
                        self.timing_counts['wolf_observe_time'] += 1

                dog_obs = next_dog_obs
                dog_pen = next_dog_pen
                wolf_obs = next_wolf_obs
                wolf_pen = next_wolf_pen

                dog_episode_reward += dog_reward
                wolf_episode_reward += wolf_reward

                self.global_step += 1

                if self.render_enabled and not getattr(self.simulator, "headless", True):
                    if self.global_step % render_stride == 0:
                        t0 = time.perf_counter()
                        self.simulator.render(fps=0)
                        t1 = time.perf_counter()
                        self.timing_stats['render_time'] += (t1 - t0)
                        self.timing_counts['render_time'] += 1

                if info.get("done", False):
                    break

            self.dog_agent.episode_end(dog_episode_reward)
            if self.wolf_agent is not None:
                self.wolf_agent.episode_end(wolf_episode_reward)

            stats = self.simulator.get_stats()
            log_entry = EpisodeLog(
                episode=episode,
                steps=stats["step_count"],
                dog_reward=dog_episode_reward,
                wolf_reward=wolf_episode_reward,
                sheep_in_pen=stats["sheep_in_pen"],
                sheep_remaining=stats["sheep_remaining"],
            )

            history.append(log_entry)

            if log_interval > 0 and (episode + 1) % log_interval == 0:
                if self.log_callback is not None:
                    self.log_callback(log_entry)
            
            # Save checkpoint periodically
            if self.save_dir is not None and self.save_every_episodes > 0:
                if (episode + 1) % self.save_every_episodes == 0:
                    self.save_checkpoint(episode + 1)

            if quit_requested:
                break

        return history

    def _process_window_events(self) -> bool:
        """Handle pygame window events and return True if quit was requested."""
        
        
        quit_requested = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                self.render_enabled = not self.render_enabled
                state = "enabled" if self.render_enabled else "disabled"
                print(f"[trainer] Rendering {state} (toggle with 'h').", flush=True)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                config.DEBUG_SHOW_OBSERVATIONS = not config.DEBUG_SHOW_OBSERVATIONS
                config.DEBUG_SHOW_PEN_DIRECTION = not config.DEBUG_SHOW_PEN_DIRECTION
                state = "enabled" if config.DEBUG_SHOW_OBSERVATIONS else "disabled"
                print(f"[trainer] Debug visualization {state} (toggle with 'd').", flush=True)
            elif event.type == pygame.QUIT:
                quit_requested = True

        if quit_requested:
            print("[trainer] Quit event received; stopping training loop.", flush=True)

        return quit_requested

    def evaluate(
        self,
        num_episodes: int,
        deterministic: bool = True,
    ) -> Tuple[float, float]:
        prev_training_mode = getattr(self.dog_agent, "training_mode", None)
        restore_mode = False
        if deterministic and hasattr(self.dog_agent, "set_eval_mode"):
            self.dog_agent.set_eval_mode(True)
            restore_mode = prev_training_mode is not None

        total_reward = 0.0
        total_steps = 0
        quit_requested = False
        render_stride = self._render_stride if self._render_stride > 0 else 1
        episodes_completed = 0

        for _ in range(num_episodes):
            (dog_obs, dog_pen), (wolf_obs, wolf_pen) = self.simulator.reset()
            episode_reward = 0.0

            for _ in range(self.max_steps):
                if self._allow_render_toggle and self._process_window_events():
                    quit_requested = True
                    break

                dog_action = self.dog_agent.act(dog_obs, dog_pen)
                if self.wolf_agent is not None:
                    wolf_action = self.wolf_agent.act(wolf_obs, wolf_pen)
                else:
                    wolf_action = WolfAction.zero()

                (
                    dog_obs,
                    dog_pen,
                    dog_reward,
                    wolf_obs,
                    wolf_pen,
                    _,
                    info,
                ) = self.simulator.step(dog_action, wolf_action)

                episode_reward += dog_reward
                total_steps += 1
                self.global_step += 1

                if self.render_enabled and not getattr(self.simulator, "headless", True):
                    if self.global_step % render_stride == 0:
                        self.simulator.render(fps=0)

                if info.get("done", False):
                    break

            total_reward += episode_reward
            episodes_completed += 1

            if quit_requested:
                break

        if restore_mode and hasattr(self.dog_agent, "set_eval_mode") and prev_training_mode is not None:
            self.dog_agent.set_eval_mode(not prev_training_mode)

        divisor = max(episodes_completed, 1)
        avg_reward = total_reward / divisor
        avg_steps = total_steps / divisor
        return avg_reward, avg_steps
    
    def print_timing_stats(self) -> None:
        """Print timing statistics for profiling."""
        print("\n" + "=" * 70)
        print("TIMING STATISTICS (Trainer)")
        print("=" * 70)
        for key in sorted(self.timing_stats.keys()):
            total_time = self.timing_stats[key]
            count = self.timing_counts[key]
            if count > 0:
                avg_time = total_time / count
                print(f"{key:25s}: Total={total_time:8.3f}s  Avg={avg_time*1000:8.3f}ms  Count={count:8d}")
            else:
                print(f"{key:25s}: No calls")
        print("=" * 70)
    
    def reset_timing_stats(self) -> None:
        """Reset timing statistics."""
        for key in self.timing_stats.keys():
            self.timing_stats[key] = 0.0
            self.timing_counts[key] = 0
