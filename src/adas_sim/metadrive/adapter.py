from metadrive.manager.traffic_manager import TrafficMode

from adas_sim.map.map_loader import MapLoader
from adas_sim.scenarios.scenario_configurator import ScenarioConfigurator, ScenarioMetaDriveConfig
from adas_sim.metadrive.indian_env import IndianTrafficMetaDriveEnv


class MetaDriveSimulator:
    """
    Adapter between our ADAS project and MetaDrive.

    Responsibilities:
    - Convert ADAS scenarios into physical MetaDrive maps.
    - Configure traffic density.
    - Configure traffic mode.
    - Configure vehicle spawn position and destination per scenario.
    - Keep manual driving handled by our VehicleController.
    """

    def __init__(
        self,
        render=True,
        manual=False,
        scenario=None,
        **env_config
    ):
        self.manual = manual
        self.scenario = (
            scenario.strip().lower()
            if isinstance(scenario, str)
            else "straight"
        )

        # ========================================================
        # SCENARIO CONFIGURATOR
        # ========================================================

        self.configurator = ScenarioConfigurator()
        self.scenario_config: ScenarioMetaDriveConfig = self.configurator.get_config(self.scenario)

        # ========================================================
        # DETERMINE PHYSICAL MAP
        # ========================================================

        physical_map = self.scenario_config.map_name

        # ========================================================
        # TRAFFIC DENSITY (use scenario config as default)
        # ========================================================

        traffic_density = env_config.get(
            "traffic_density",
            self.scenario_config.traffic_density
        )

        traffic_density = self._validate_traffic_density(traffic_density)

        # ========================================================
        # TRAFFIC MIX (for Indian road conditions)
        # ========================================================

        # Build traffic mix from scenario config
        self.traffic_mix = self._build_traffic_mix()

        # ========================================================
        # DEFAULT METADRIVE CONFIG
        # ========================================================

        default_config = {
            "num_scenarios": 1,
            "start_seed": 0,
            "use_render": render,
            "manual_control": False,
            "map": physical_map,
            "traffic_density": traffic_density,
            "traffic_mode": TrafficMode.Trigger,
            "image_observation": False,
            "vehicle_config": {
                "show_side_detector": False,
                "show_lidar": False,
                "enable_reverse": True,
            },
            "random_lane_width": False,
            "random_lane_num": False,
        }

        # ========================================================
        # MERGE USER CONFIGURATION
        # ========================================================

        for key, value in env_config.items():
            if key == "vehicle_config":
                default_vehicle_config = default_config["vehicle_config"]
                default_vehicle_config.update(value)
            else:
                default_config[key] = value

        # ========================================================
        # FORCE CORRECT VALUES FROM SCENARIO
        # ========================================================

        default_config["map"] = physical_map
        default_config["traffic_density"] = traffic_density
        default_config["manual_control"] = False

        # ========================================================
        # PRINT CONFIGURATION
        # ========================================================

        print()
        print("=" * 60)
        print("METADRIVE CONFIGURATION")
        print("=" * 60)
        print(f"Scenario          : {self.scenario}")
        print(f"Physical Map      : {physical_map}")
        print(f"Maneuver          : {self.scenario_config.maneuver}")
        print(f"Traffic Density   : {traffic_density:.2f}")
        print(f"Traffic Mode      : {default_config.get('traffic_mode')}")
        print(f"Traffic Mix       : {self.traffic_mix}")
        print(f"Render            : {default_config['use_render']}")
        print(f"Vehicle Spawn     : {self.scenario_config.vehicle_spawn.position}")
        print(f"Vehicle Heading   : {self.scenario_config.vehicle_spawn.heading:.2f} rad")
        print(f"Destination       : {self.scenario_config.destination.position}")
        print("=" * 60)
        print()

        # ========================================================
        # CREATE METADRIVE ENVIRONMENT
        # ========================================================

        # Add traffic_mix to config for custom environment
        default_config["traffic_mix"] = self.traffic_mix

        self.env = IndianTrafficMetaDriveEnv(default_config)

        # ========================================================
        # ADAS SCENARIO METADATA
        # ========================================================

        self.map_loader = MapLoader(scenario=self.scenario)
        self._vehicle_spawn_set = False

    # ============================================================
    # TRAFFIC DENSITY VALIDATION
    # ============================================================

    @staticmethod
    def _validate_traffic_density(traffic_density):
        """
        MetaDrive traffic density is expected in the range 0.0 to 1.0.
        """
        try:
            density = float(traffic_density)
        except (TypeError, ValueError):
            raise ValueError("traffic_density must be a number between 0.0 and 1.0.")
        if density < 0.0 or density > 1.0:
            raise ValueError("traffic_density must be between 0.0 and 1.0.")
        return density

    # ============================================================
    # RESET
    # ============================================================

    def reset(self):
        observation, info = self.env.reset()

        # Set vehicle spawn position and destination after reset
        if not self._vehicle_spawn_set:
            self._set_vehicle_spawn_and_destination()
            self._vehicle_spawn_set = True

        return observation, info

    def _set_vehicle_spawn_and_destination(self):
        """Set vehicle initial position and navigation target."""
        vehicle = self.env.agent
        if vehicle is None:
            return

        spawn = self.scenario_config.vehicle_spawn
        dest = self.scenario_config.destination

        # Set vehicle position and heading
        # MetaDrive uses (x, y) for position, heading in radians
        try:
            vehicle.set_position(spawn.position, spawn.heading)
            print(f"[SPAWN] Vehicle positioned at {spawn.position} with heading {spawn.heading:.2f}")
        except Exception as e:
            print(f"[SPAWN] Warning: Could not set position: {e}")

        # Set navigation destination
        try:
            # MetaDrive vehicles have a navigation system
            # We can set the target lane or destination
            if hasattr(vehicle, "set_destination"):
                vehicle.set_destination(dest.position)
                print(f"[DEST] Navigation target set to {dest.position}")
            elif hasattr(vehicle, "navigation") and vehicle.navigation is not None:
                vehicle.navigation.set_destination(dest.position)
                print(f"[DEST] Navigation target set to {dest.position}")
        except Exception as e:
            print(f"[DEST] Warning: Could not set destination: {e}")

    # ============================================================
    # STEP
    # ============================================================

    def step(self, action=None):
        return self.env.step(action)

    # ============================================================
    # VEHICLE
    # ============================================================

    def get_vehicle(self):
        return self.env.agent

    # ============================================================
    # CAMERA
    # ============================================================

    def get_camera_image(self):
        camera = self.env.engine.get_sensor("main_camera")
        if camera is None:
            return None
        return camera.perceive(to_float=False)

    # ============================================================
    # LANE INFORMATION
    # ============================================================

    def get_lane_info(self, position):
        return self.map_loader.get_lane_info(position)

    # ============================================================
    # INTERSECTION INFORMATION
    # ============================================================

    def get_intersection_info(self, position):
        return self.map_loader.get_intersection_info(position)

    # ============================================================
    # SCENARIO SUMMARY
    # ============================================================

    def get_scenario_summary(self):
        return self.map_loader.get_scenario_config()

    def get_scenario_config(self):
        """Get the full scenario configuration."""
        return self.scenario_config

    # ============================================================
    # CLOSE
    # ============================================================

    def close(self):
        if self.env is not None:
            self.env.close()

    # ============================================================
    # TRAFFIC MIX HELPERS
    # ============================================================

    def _build_traffic_mix(self) -> dict:
        """Build traffic mix configuration from scenario cross_traffic config."""
        cross_traffic = self.scenario_config.cross_traffic

        if not cross_traffic.enabled:
            return {}

        # Map scenario vehicle types to traffic mix
        # Default distribution for Indian urban traffic
        vehicle_types = cross_traffic.vehicle_types

        # Default probabilities based on Indian urban traffic patterns
        type_probs = {
            "car": 0.45,
            "two_wheeler": 0.35,
            "auto_rickshaw": 0.10,
            "bus": 0.07,
            "truck": 0.03,
        }

        # Filter to only include types specified in scenario config
        traffic_mix = {}
        for vtype in vehicle_types:
            if vtype in type_probs:
                traffic_mix[vtype] = type_probs[vtype]

        # Normalize
        total = sum(traffic_mix.values())
        if total > 0:
            traffic_mix = {k: v / total for k, v in traffic_mix.items()}

        return traffic_mix