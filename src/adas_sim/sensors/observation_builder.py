import numpy as np


class ObservationBuilder:

    def __init__(self, max_speed=40.0):

        self.max_speed = max_speed
        self.observation_size = 242

        print(
            f"Observation Builder Initialized: "
            f"{self.observation_size} dimensions"
        )

    def build(self, lidar_data, vehicle_state):

        lidar_data = np.asarray(
            lidar_data,
            dtype=np.float32
        )

        speed = np.clip(
            vehicle_state["speed"] / self.max_speed,
            0.0,
            1.0
        )

        heading = vehicle_state["heading"]

        observation = np.concatenate(
            [
                lidar_data,
                [speed],
                [heading]
            ]
        )

        return observation.astype(np.float32)