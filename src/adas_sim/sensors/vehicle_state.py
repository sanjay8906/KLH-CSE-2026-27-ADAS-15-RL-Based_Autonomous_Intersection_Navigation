import numpy as np


class VehicleState:

    def __init__(self):
        print("Vehicle State Initialized")

    def process(self, vehicle):

        state = {
            "position": np.asarray(vehicle.position, dtype=np.float32),
            "speed": float(vehicle.speed),
            "heading": float(vehicle.heading_theta),
        }

        return state