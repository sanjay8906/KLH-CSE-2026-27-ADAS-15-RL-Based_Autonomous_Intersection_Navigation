import numpy as np


class GPSSensor:
    def __init__(self):
        print("GPS Sensor Initialized")
        self.last_position = None

    def process(self, vehicle):
        """
        Extract GPS-like data from vehicle state.
        Since MetaDrive does not provide actual GPS coordinates,
        we approximate GPS from the vehicle's position.
        Returns a dictionary with latitude, longitude, altitude, and speed.
        For simplicity, we treat the position as local ENU coordinates and
        output them as if they were GPS (lat, lon, alt) in degrees/meters.
        In a real scenario, you would convert from local coordinates to GPS
        using a reference point.
        """
        position = np.asarray(vehicle.position, dtype=np.float32)
        speed = float(vehicle.speed)

        # If we had a reference point, we could convert to lat/lon.
        # For now, we just output the position as GPS-like values.
        # We assume position[0] is easting, position[1] is northing, position[2] is altitude.
        # We'll treat easting as longitude, northing as latitude, and altitude as altitude.
        # This is not physically accurate but sufficient for simulation.
        gps_data = {
            "latitude": position[1],   # northing as latitude
            "longitude": position[0],  # easting as longitude
            "altitude": position[2] if len(position) > 2 else 0.0,
            "speed": speed             # speed in m/s
        }

        return gps_data