"""
Custom MetaDrive Environment with Indian Traffic Manager

Subclasses MetaDriveEnv to use IndianTrafficManager instead of the default PGTrafficManager,
enabling configurable vehicle type distributions for Indian road conditions.
"""

from metadrive.envs.metadrive_env import MetaDriveEnv
from metadrive.manager.pg_map_manager import PGMapManager
from metadrive.manager.object_manager import TrafficObjectManager

from adas_sim.metadrive.traffic_manager import IndianTrafficManager


class IndianTrafficMetaDriveEnv(MetaDriveEnv):
    """
    MetaDrive environment with Indian traffic manager.

    This environment uses IndianTrafficManager which supports configurable
    vehicle type distributions (cars, two-wheelers, auto-rickshaws, buses, trucks)
    for realistic Indian road conditions.
    """

    def __init__(self, config: dict = None):
        # Extract traffic_mix before parent init (parent validates config keys)
        config = config or {}
        self._traffic_mix = config.pop("traffic_mix", {})
        super(IndianTrafficMetaDriveEnv, self).__init__(config)

    def setup_engine(self):
        """Override to use IndianTrafficManager instead of PGTrafficManager."""
        # Call parent's parent (BaseEnv) setup_engine
        super(MetaDriveEnv, self).setup_engine()

        # Register managers with Indian traffic manager
        self.engine.register_manager("map_manager", PGMapManager())
        self.engine.register_manager("traffic_manager", IndianTrafficManager())

        # Set traffic mix on the traffic manager
        if hasattr(self.engine, "global_config"):
            self.engine.global_config["traffic_mix"] = self._traffic_mix

        if abs(self.config["accident_prob"] - 0) > 1e-2:
            self.engine.register_manager("object_manager", TrafficObjectManager())

        print("[IndianTrafficMetaDriveEnv] Registered IndianTrafficManager")


def create_indian_traffic_env(config: dict = None) -> IndianTrafficMetaDriveEnv:
    """Factory function to create IndianTrafficMetaDriveEnv instance."""
    return IndianTrafficMetaDriveEnv(config)


if __name__ == "__main__":
    print("IndianTrafficMetaDriveEnv module loaded successfully")