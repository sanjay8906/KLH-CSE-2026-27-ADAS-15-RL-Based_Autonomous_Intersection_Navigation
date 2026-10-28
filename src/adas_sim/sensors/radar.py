import numpy as np


class RadarSensor:
    def __init__(self):
        print("Radar Sensor Initialized")
        self.last_lidar_data = None
        self.last_lidar_indices = None
        self.dt = 0.1  # time step
        # Temporal smoothing for velocity estimates
        self.velocity_history = {}  # index -> list of recent velocities
        self.max_history = 5  # frames to average over

    def process(self, lidar_data, ego_speed=0.0, ego_heading=0.0):
        """
        Simulate radar data from LiDAR point cloud.
        We detect peaks in the LiDAR data as potential objects and estimate
        their radial velocity using Doppler shift (change in distance over time).
        Returns a list of detected objects, each with distance and velocity.

        Args:
            lidar_data: LiDAR distances in meters (240 rays, 360°)
            ego_speed: Ego vehicle speed in m/s (forward positive)
            ego_heading: Ego vehicle heading in radians
        """
        lidar_data = np.asarray(lidar_data, dtype=np.float32)
        num_lasers = len(lidar_data)

        # LiDAR angle for each index (index 0 = front = 0 rad)
        angle_per_laser = 2.0 * np.pi / num_lasers

        # Valid range: not too close (avoid self-detection), not too far
        valid_mask = (lidar_data > 2.5) & (lidar_data < 50.0)
        valid_indices = np.where(valid_mask)[0]
        valid_distances = lidar_data[valid_mask]

        # If we have no previous data, we cannot compute velocity.
        if self.last_lidar_data is None:
            self.last_lidar_data = lidar_data.copy()
            self.last_lidar_indices = valid_indices.copy()
            # Return dummy detections
            detections = []
            for i, dist in enumerate(valid_distances[:5]):  # limit to 5 detections
                detections.append({
                    "distance": float(dist),
                    "velocity": 0.0,  # unknown without previous frame
                    "index": int(valid_indices[i])
                })
            return detections

        # Compute change in distance for each valid point
        # We match by index since LiDAR rays are fixed
        delta = lidar_data - self.last_lidar_data

        # Standard radar convention: negative radial velocity = approaching
        # delta = current - previous, so if distance decreased (approaching), delta < 0
        # radial_vel = -delta / dt gives: negative = approaching, positive = receding
        radial_velocity = -delta / self.dt

        # Compensate for ego motion:
        # For each ray, the ego motion contributes ego_speed * cos(bearing) to the radial velocity
        # (since ego moving forward reduces distance to objects ahead)
        # Object's actual radial velocity (in world frame, relative to static world) =
        #   measured_radial_vel - ego_radial_contribution
        #   = radial_velocity - ego_speed * cos(bearing)
        # where bearing is the angle of the LiDAR ray

        detections = []
        for i in valid_indices:
            dist = lidar_data[i]
            measured_radial_vel = radial_velocity[i]

            # Bearing of this LiDAR ray (0 = front, positive = left)
            bearing = i * angle_per_laser
            if bearing > np.pi:
                bearing -= 2.0 * np.pi

            # Ego motion contribution to radial velocity (forward motion reduces distance ahead)
            ego_radial_contrib = ego_speed * np.cos(bearing)

            # Object's actual radial velocity in world frame (relative to static world)
            # If object is stationary in world, this should be ~0
            obj_radial_vel = measured_radial_vel - ego_radial_contrib

            # Temporal smoothing: maintain history per ray index
            if i not in self.velocity_history:
                self.velocity_history[i] = []
            self.velocity_history[i].append(obj_radial_vel)
            if len(self.velocity_history[i]) > self.max_history:
                self.velocity_history[i].pop(0)

            # Use median to reject outliers (more robust than mean for radar)
            smoothed_vel = float(np.median(self.velocity_history[i]))

            # Filter: only report objects with significant motion relative to world
            # Higher threshold (3 m/s = 10.8 km/h) to filter noise from LiDAR differencing
            # Also require consistency: at least 3 frames in history
            if abs(smoothed_vel) > 3.0 and len(self.velocity_history[i]) >= 3:
                # Additional sanity check: velocity should be reasonable for traffic
                # Max reasonable speed: 40 m/s = 144 km/h
                if abs(smoothed_vel) <= 40.0:
                    detections.append({
                        "distance": float(dist),
                        "velocity": smoothed_vel,  # Object radial velocity in world frame
                        "index": int(i)
                    })

        # Limit number of detections
        detections = detections[:10]

        # Clean up history for indices no longer valid
        valid_set = set(valid_indices)
        self.velocity_history = {k: v for k, v in self.velocity_history.items() if k in valid_set}

        # Update last lidar data
        self.last_lidar_data = lidar_data.copy()
        self.last_lidar_indices = valid_indices.copy()

        return detections

    def reset(self):
        self.last_lidar_data = None
        self.last_lidar_indices = None
        self.velocity_history = {}