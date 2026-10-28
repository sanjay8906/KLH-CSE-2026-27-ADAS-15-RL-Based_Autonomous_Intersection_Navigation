import numpy as np


class LidarSensor:

    def __init__(self, num_lasers=240, max_range=50.0):

        self.num_lasers = num_lasers
        self.max_range = max_range  # meters

        print(f"LiDAR Initialized: {self.num_lasers} rays, max_range={self.max_range}m")

    def process(self, observation):

        observation = np.asarray(observation, dtype=np.float32)

        if observation.ndim != 1:
            raise ValueError(
                f"Expected 1D observation, got shape {observation.shape}"
            )

        if len(observation) < self.num_lasers:
            raise ValueError(
                f"Observation has only {len(observation)} values, "
                f"but {self.num_lasers} LiDAR values were requested."
            )

        # MetaDrive's LidarStateObservation places the
        # LiDAR cloud points at the end of the observation.
        # These are HIT FRACTIONS (0.0 to 1.0), not distances.
        # Actual distance = hit_fraction * max_range
        hit_fractions = observation[-self.num_lasers:]

        # Convert hit fractions to actual distances (meters)
        lidar_data = hit_fractions * self.max_range

        return lidar_data