import numpy as np


class UltrasonicSensor:
    def __init__(self, fov_degrees=30.0, max_range=5.0):
        print(f"Ultrasonic Sensor Initialized: FOV={fov_degrees}°, max range={max_range}m")
        self.fov = np.radians(fov_degrees)
        self.max_range = max_range
        # Assuming the LiDAR array covers 360 degrees with equal angular spacing
        # We will need to know the number of lasers to compute angles.
        # We'll store the number of lasers from the first process call.
        self.num_lasers = None

    def process(self, lidar_data):
        """
        Compute ultrasonic distance as the minimum distance within a forward cone.
        We assume the ultrasonic sensor is mounted at the front of the vehicle,
        pointing straight ahead (0 degrees azimuth).
        We LiDAR data is assumed to be an array of distances with equal angular spacing
        covering 360 degrees, starting from the front (0 degrees) and going counter-clockwise?
        The exact orientation depends on the LiDAR setup. For simplicity, we assume
        the LiDAR data is ordered such that index 0 corresponds to the front of the vehicle.
        We will compute the indices that fall within the forward field of view.
        """
        lidar_data = np.asarray(lidar_data, dtype=np.float32)

        if self.num_lasers is None:
            self.num_lasers = len(lidar_data)
            # Compute angular resolution
            self.angle_per_laser = 2.0 * np.pi / self.num_lasers

        # Determine indices that fall within the forward FOV
        # We assume the forward direction corresponds to angles [-fov/2, +fov/2] around 0 radians.
        # Since our LiDAR array starts at index 0 for front (0 rad), we need to wrap around.
        # We'll compute the indices for angles from -fov/2 to +fov/2.
        half_fov_rad = self.fov / 2.0
        # Convert to index offset from front
        offset = int(half_fov_rad / self.angle_per_laser)
        # Indices from -offset to +offset, wrapping around the array.
        indices = []
        for i in range(-offset, offset + 1):
            idx = i % self.num_lasers
            indices.append(idx)

        # Extract distances within the FOV
        fov_distances = lidar_data[indices]
        # Apply maximum range
        fov_distances = np.where(fov_distances > self.max_range, self.max_range, fov_distances)

        # The ultrasonic reading is the minimum distance in the FOV
        min_distance = np.min(fov_distances) if len(fov_distances) > 0 else self.max_range

        ultrasonic_data = {
            "distance": float(min_distance),
            "max_range": self.max_range,
            "fov_degrees": np.degrees(self.fov)
        }

        return ultrasonic_data