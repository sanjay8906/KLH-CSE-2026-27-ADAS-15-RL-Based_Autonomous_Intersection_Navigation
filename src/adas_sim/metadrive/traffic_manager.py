"""
Custom Traffic Manager for Indian Road Conditions

Extends MetaDrive's PGTrafficManager to support configurable vehicle type distributions
for mixed-density traffic scenarios (cars, two-wheelers, auto-rickshaws, buses, trucks).
"""

from metadrive.manager.traffic_manager import PGTrafficManager
from metadrive.component.vehicle.vehicle_type import random_vehicle_type


class IndianTrafficManager(PGTrafficManager):
    """
    Traffic manager with configurable vehicle type distribution for Indian roads.

    Vehicle type mapping:
    - "car" / "sedan" / "hatchback" -> DefaultVehicle / MVehicle (medium cars)
    - "two_wheeler" / "motorcycle" / "scooter" -> SVehicle (small)
    - "auto_rickshaw" / "tuk_tuk" -> SVehicle (small, three-wheeler)
    - "bus" / "minibus" -> LVehicle (large)
    - "truck" / "lorry" -> XLVehicle (extra large)

    The traffic mix is configured via global_config["traffic_mix"] which should be
    a dict mapping vehicle type names to probabilities, e.g.:
    {
        "car": 0.5,
        "two_wheeler": 0.3,
        "auto_rickshaw": 0.1,
        "bus": 0.07,
        "truck": 0.03
    }
    """

    # Map our traffic type names to MetaDrive vehicle type keys
    VEHICLE_TYPE_MAP = {
        "car": "default",           # DefaultVehicle (4.5m)
        "sedan": "m",               # MVehicle (4.6m)
        "hatchback": "s",           # SVehicle (4.3m) - smaller car
        "two_wheeler": "s",         # SVehicle (4.3m) - motorcycle/scooter
        "motorcycle": "s",
        "scooter": "s",
        "auto_rickshaw": "s",       # SVehicle - three wheeler
        "tuk_tuk": "s",
        "bus": "l",                 # LVehicle (4.87m) - bus
        "minibus": "l",
        "truck": "xl",              # XLVehicle (5.74m) - truck
        "lorry": "xl",
    }

    # Default Indian urban traffic mix (approximate)
    DEFAULT_TRAFFIC_MIX = {
        "car": 0.45,
        "two_wheeler": 0.35,
        "auto_rickshaw": 0.10,
        "bus": 0.07,
        "truck": 0.03,
    }

    def __init__(self):
        super(IndianTrafficManager, self).__init__()
        # Will be set after engine is available
        self._traffic_mix = None
        self._vehicle_type_probs = None

    def _init_traffic_mix(self):
        """Initialize traffic mix from global config."""
        if self._traffic_mix is not None:
            return

        # Get traffic mix from global config, fallback to default
        traffic_mix = self.engine.global_config.get("traffic_mix", self.DEFAULT_TRAFFIC_MIX)

        # Convert to MetaDrive vehicle type probabilities
        # MetaDrive random_vehicle_type expects probabilities for: s, m, l, xl, default
        metadrive_types = ["s", "m", "l", "xl", "default"]
        probs = [0.0] * 5

        for traffic_type, prob in traffic_mix.items():
            metadrive_key = self.VEHICLE_TYPE_MAP.get(traffic_type.lower(), "default")
            if metadrive_key in metadrive_types:
                idx = metadrive_types.index(metadrive_key)
                probs[idx] += prob

        # Normalize to sum to 1.0
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        else:
            # Fallback to MetaDrive default
            probs = [0.2, 0.3, 0.3, 0.2, 0.0]

        self._traffic_mix = traffic_mix
        self._vehicle_type_probs = probs

        print(f"[IndianTrafficManager] Traffic mix: {traffic_mix}")
        print(f"[IndianTrafficManager] MetaDrive probs (s,m,l,xl,default): {[round(p, 3) for p in probs]}")

    def random_vehicle_type(self):
        """Return a random vehicle type based on configured traffic mix."""
        self._init_traffic_mix()
        return random_vehicle_type(self.np_random, self._vehicle_type_probs)

    def set_traffic_mix(self, traffic_mix: dict):
        """Update traffic mix at runtime."""
        self._traffic_mix = traffic_mix
        self._vehicle_type_probs = None  # Will be recomputed on next call
        self._init_traffic_mix()


def create_indian_traffic_manager():
    """Factory function to create IndianTrafficManager instance."""
    return IndianTrafficManager()


if __name__ == "__main__":
    # Test the traffic mix conversion
    print("Testing IndianTrafficManager traffic mix conversion...")

    # Simulate the conversion logic
    VEHICLE_TYPE_MAP = {
        "car": "default",
        "sedan": "m",
        "hatchback": "s",
        "two_wheeler": "s",
        "motorcycle": "s",
        "scooter": "s",
        "auto_rickshaw": "s",
        "tuk_tuk": "s",
        "bus": "l",
        "minibus": "l",
        "truck": "xl",
        "lorry": "xl",
    }

    DEFAULT_TRAFFIC_MIX = {
        "car": 0.45,
        "two_wheeler": 0.35,
        "auto_rickshaw": 0.10,
        "bus": 0.07,
        "truck": 0.03,
    }

    metadrive_types = ["s", "m", "l", "xl", "default"]
    probs = [0.0] * 5

    for traffic_type, prob in DEFAULT_TRAFFIC_MIX.items():
        metadrive_key = VEHICLE_TYPE_MAP.get(traffic_type.lower(), "default")
        if metadrive_key in metadrive_types:
            idx = metadrive_types.index(metadrive_key)
            probs[idx] += prob

    total = sum(probs)
    if total > 0:
        probs = [p / total for p in probs]

    print(f"Default traffic mix: {DEFAULT_TRAFFIC_MIX}")
    print(f"MetaDrive probs (s,m,l,xl,default): {[round(p, 3) for p in probs]}")
    print(f"Sum: {sum(probs):.3f}")