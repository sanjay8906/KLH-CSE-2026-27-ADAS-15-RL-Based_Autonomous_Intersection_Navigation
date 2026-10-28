from adas_sim.metadrive.adapter import MetaDriveSimulator
from adas_sim.sensors.lidar import LidarSensor
import numpy as np

simulator = MetaDriveSimulator(
    render=False,
    manual=False,
    scenario='straight',
    traffic_density=0.1,
    num_scenarios=1,
    image_observation=False,
)

obs, info = simulator.reset()
print(f"Observation type: {type(obs)}")
print(f"Observation shape: {obs.shape if hasattr(obs, 'shape') else 'N/A'}")
print(f"Observation len: {len(obs) if hasattr(obs, '__len__') else 'N/A'}")

lidar = LidarSensor(num_lasers=240)
lidar_data = lidar.process(obs)

print(f"\nLiDAR data shape: {lidar_data.shape}")
print(f"LiDAR min: {np.min(lidar_data):.2f}")
print(f"LiDAR max: {np.max(lidar_data):.2f}")
print(f"LiDAR mean: {np.mean(lidar_data):.2f}")
print(f"LiDAR median: {np.median(lidar_data):.2f}")

# Check how many points are < 2.5
close_points = lidar_data[lidar_data < 2.5]
print(f"Points < 2.5m: {len(close_points)} out of {len(lidar_data)}")
if len(close_points) > 0:
    print(f"  Min close: {np.min(close_points):.2f}")
    print(f"  Max close: {np.max(close_points):.2f}")

# Check front rays (indices around 0)
front_rays = lidar_data[:10]
print(f"\nFront 10 rays: {front_rays}")

# Check if there are any 0 or negative values
zero_or_neg = lidar_data[lidar_data <= 0]
print(f"\nZero or negative values: {len(zero_or_neg)}")

# Check distribution
hist, bins = np.histogram(lidar_data, bins=20, range=(0, 50))
print("\nDistance distribution:")
for h, b in zip(hist, bins[:-1]):
    if h > 0:
        print(f"  {b:.1f}-{b+2.5:.1f}m: {h}")

simulator.close()