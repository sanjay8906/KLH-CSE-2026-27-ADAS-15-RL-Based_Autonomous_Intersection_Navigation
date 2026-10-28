import numpy as np


class IMUSensor:
    def __init__(self):
        print("IMU Sensor Initialized")
        self.last_velocity = None
        self.last_heading = None
        self.dt = 0.1  # assume time step of 0.1 seconds; adjust based on actual simulation step

    def process(self, vehicle):
        """
        Extract IMU data: linear acceleration and angular velocity.
        We approximate acceleration from change in velocity over time,
        and angular velocity from change in heading over time.
        If the vehicle provides acceleration and angular velocity directly, we could use those.
        For now, we compute from differences.
        """
        velocity = np.asarray(vehicle.velocity, dtype=np.float32) if hasattr(vehicle, 'velocity') else np.asarray([vehicle.speed, 0.0, 0.0], dtype=np.float32)
        heading = float(vehicle.heading_theta) if hasattr(vehicle, 'heading_theta') else 0.0

        # Compute linear acceleration (change in velocity over time)
        if self.last_velocity is not None:
            acceleration = (velocity - self.last_velocity) / self.dt
        else:
            acceleration = np.zeros_like(velocity)

        # Compute angular velocity (change in heading over time)
        if self.last_heading is not None:
            angular_velocity = (heading - self.last_heading) / self.dt
        else:
            angular_velocity = 0.0

        # Store current values for next step
        self.last_velocity = velocity.copy()
        self.last_heading = heading

        imu_data = {
            "linear_acceleration": acceleration.tolist(),  # [ax, ay, az]
            "angular_velocity": angular_velocity           # scalar (yaw rate) or vector if we had pitch/roll
        }

        return imu_data