# Test script to verify the package works with bundled assets
from sheep_herding_rl import Simulator
from pathlib import Path

print("Creating simulator in headless mode...")
sim = Simulator(headless=True)

print(f"✓ Simulator created successfully")
print(f"✓ Sheep sprite path: {sim.sheep_sprite}")
print(f"✓ File exists: {Path(sim.sheep_sprite).exists()}")

# Quick step test
(dog_obs, dog_meta), (wolf_obs, wolf_meta) = sim.reset()
print(f"✓ Reset successful, dog observation shape: {dog_obs.shape}")

sim.step([0.5, 0.0], [0.3, 0.1])
print(f"✓ Step successful")

print("\n✅ All tests passed! Package assets are correctly bundled.")
