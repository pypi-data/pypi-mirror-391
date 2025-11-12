# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2025-11-12

### Added
- Export agent configuration classes: `PPOAgentConfig`, `SACAgentConfig`, `TD3AgentConfig`
- Export `EpisodeLog` class from trainers for logging training episodes

## [1.0.1] - 2025-11-12

### Added
- Exported `RandomAgent` from main package for easier access

### Fixed
- Image assets now use absolute paths from package installation directory
- Images properly bundled in distribution (grass2.jpg, wood.jpg, sprites)
- Headless mode no longer crashes when loading textures

## [1.0] - 2025-11-12

### Added
- Initial package release
- Sheep herding simulation environment
- PPO (Proximal Policy Optimization) agent implementation
- SAC (Soft Actor-Critic) agent implementation
- TD3 (Twin Delayed DDPG) agent implementation
- Dog and Wolf agent classes
- On-policy and off-policy trainers
- Local and global observation modes
- Configurable observation grid with Gaussian splatting
- Debug visualization modes
- Observation utilities and map utilities
- Replay buffers for off-policy algorithms
- Rollout buffers for on-policy algorithms
- Package setup files for PyPI distribution
- Comprehensive documentation (README, INSTALL, USAGE, BUILD guides)
- Build automation script
- MIT License

### Features
- Multi-agent support (dog and wolf)
- Flexible observation system (local ego-centric or global view)
- Multiple RL algorithm implementations
- Real-time visualization with Pygame
- Configurable simulation parameters
- GPU acceleration support via PyTorch

[Unreleased]: https://github.com/dzijo/ferit-hackathon/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/dzijo/ferit-hackathon/compare/v1.0...v1.0.1
[1.0]: https://github.com/dzijo/ferit-hackathon/releases/tag/v1.0
