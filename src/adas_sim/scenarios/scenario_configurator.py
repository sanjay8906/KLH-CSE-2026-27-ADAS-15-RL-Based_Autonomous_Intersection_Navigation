"""
Scenario Configurator for MetaDrive Intersection Scenarios

Maps each ADAS scenario to specific MetaDrive configurations:
- Vehicle spawn position and orientation
- Target destination
- Traffic light configuration
- Cross-traffic setup
- Mixed-density traffic for Indian road conditions

Based on MetaDrive 0.4.3 map layouts:
- X (4-way): Intersection center ~(50, 7), approaches from 4 directions
- T (T-junction): Intersection center ~(50, 7), 3 approaches
- Y (Y-junction): Intersection center ~(50, 7), 3 approaches (Y-shaped)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple
import numpy as np

from adas_sim.scenarios.intersection_scenario import IntersectionScenario, INTERSECTION_SCENARIOS


@dataclass
class VehicleSpawnConfig:
    """Configuration for vehicle spawn position and orientation."""
    position: Tuple[float, float]  # (x, y) in world coordinates
    heading: float  # radians
    lane_index: Optional[str] = None  # MetaDrive lane identifier


@dataclass
class DestinationConfig:
    """Configuration for navigation target."""
    position: Tuple[float, float]  # (x, y) in world coordinates
    lane_index: Optional[str] = None


@dataclass
class TrafficLightConfig:
    """Configuration for traffic light at intersection."""
    position: Tuple[float, float]
    initial_state: str = "green"  # "red", "yellow", "green"
    cycle_duration: float = 30.0  # seconds for full cycle
    green_duration: float = 15.0
    yellow_duration: float = 3.0
    red_duration: float = 12.0


@dataclass
class CrossTrafficConfig:
    """Configuration for cross-traffic vehicles."""
    enabled: bool = True
    density: float = 0.1  # 0.0 to 1.0
    vehicle_types: List[str] = field(default_factory=lambda: ["car", "two_wheeler", "auto_rickshaw"])
    spawn_lanes: List[str] = field(default_factory=list)


@dataclass
class PedestrianConfig:
    """Configuration for pedestrian traffic."""
    enabled: bool = False
    density: float = 0.05
    crossing_zones: List[Tuple[float, float, float, float]] = field(default_factory=list)  # (x1, y1, x2, y2)


@dataclass
class ScenarioMetaDriveConfig:
    """Complete MetaDrive configuration for a scenario."""
    # Vehicle setup
    vehicle_spawn: VehicleSpawnConfig
    destination: DestinationConfig

    # Intersection elements
    traffic_lights: List[TrafficLightConfig] = field(default_factory=list)
    cross_traffic: CrossTrafficConfig = field(default_factory=CrossTrafficConfig)
    pedestrians: PedestrianConfig = field(default_factory=PedestrianConfig)

    # Traffic density (overall)
    traffic_density: float = 0.1

    # Map-specific
    map_name: str = "X"  # "X", "T", or "Y"

    # Scenario metadata
    scenario_name: str = "straight"
    maneuver: str = "go_straight"


class ScenarioConfigurator:
    """
    Configures MetaDrive environment for each intersection scenario.

    Maps high-level scenario definitions to low-level MetaDrive parameters
    including vehicle spawn, destination, traffic lights, and traffic patterns.
    """

    def __init__(self):
        self._configs = self._build_all_configs()

    def _build_all_configs(self) -> Dict[str, ScenarioMetaDriveConfig]:
        """Build configurations for all scenarios."""
        configs = {}

        # ============================================================
        # META DRIVE MAP X (4-way intersection) LAYOUT
        # ============================================================
        # Intersection center: ~(50, 7)
        # West approach (eastbound): y=0, 3.5, 7, lanes: '>>', '>>>'
        # East approach (westbound): y=10.5, 14, 17.5, lanes: '->', '->>'
        # South approach (northbound): x=50-87.5, lanes: '1X0_0_', '1X1_0_', '1X2_0_'
        # North approach (southbound): x=87.5-50, lanes: '-1X0_0_', '-1X1_0_', '-1X2_0_'
        # East exit: '1X1_1_' at y=7, '1X0_1_' at y=-10, '1X2_1_' at y=27.5

        # ============================================================
        # 4-WAY INTERSECTION (X map) SCENARIOS
        # ============================================================

        # Straight through 4-way intersection (west to east)
        configs["straight"] = ScenarioMetaDriveConfig(
            scenario_name="straight",
            maneuver="go_straight",
            map_name="X",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),  # On '>>>' lane, eastbound
                heading=0.0,  # Eastbound
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(100.0, 7.0),  # On '1X1_1_' lane, east exit
                lane_index="1X1_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.1,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1X1_0_", "1X0_0_", "->"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # Left turn at 4-way intersection (west to north)
        configs["left-turn"] = ScenarioMetaDriveConfig(
            scenario_name="left-turn",
            maneuver="turn_left",
            map_name="X",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),  # On '>>>' lane, eastbound
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(50.0, 60.0),  # On '-1X1_1_' or similar, north exit
                lane_index="-1X1_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.15,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw", "bus"],
                spawn_lanes=["-1X0_0_", "1X1_0_", "-1X1_0_", "1X2_0_", "->", "->>"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.08,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3), (47, 10, 53, 20)]
            )
        )

        # Right turn at 4-way intersection (west to south)
        configs["right-turn"] = ScenarioMetaDriveConfig(
            scenario_name="right-turn",
            maneuver="turn_right",
            map_name="X",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 3.5),  # On '>>>' lane, lower lane for right turn
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(50.0, -30.0),  # On '1X0_1_' or similar, south exit
                lane_index="1X0_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.1,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1X0_0_", "1X1_0_", "-1X1_0_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # Yield scenario - uncontrolled intersection
        configs["yield"] = ScenarioMetaDriveConfig(
            scenario_name="yield",
            maneuver="yield_to_cross_traffic",
            map_name="X",
            traffic_density=0.2,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(100.0, 7.0),
                lane_index="1X1_1_"
            ),
            traffic_lights=[],  # No traffic lights - yield controlled
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.2,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw", "bus"],
                spawn_lanes=["-1X0_0_", "1X1_0_", "-1X1_0_", "1X2_0_", "-1X2_0_", "->", "->>"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.1,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3), (47, 10, 53, 20), (47, -20, 53, -10)]
            )
        )

        # Stop and go - red light scenario
        configs["stop-and-go"] = ScenarioMetaDriveConfig(
            scenario_name="stop-and-go",
            maneuver="stop_and_go",
            map_name="X",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(100.0, 7.0),
                lane_index="1X1_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(
                    position=(50.0, 7.0),
                    initial_state="red",
                    cycle_duration=30.0,
                    green_duration=10.0,
                    yellow_duration=3.0,
                    red_duration=17.0
                )
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.1,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1X0_0_", "1X1_0_", "-1X1_0_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # ============================================================
        # T-JUNCTION SCENARIOS (T map)
        # ============================================================
        # T map structure: stem from south, top from east-west
        # Need to check actual T map layout

        # T-junction - vehicle on stem going to top of T
        configs["t-junction"] = ScenarioMetaDriveConfig(
            scenario_name="t-junction",
            maneuver="t_junction",
            map_name="T",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),  # On stem approach
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(100.0, 7.0),
                lane_index="1T1_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.15,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1T0_0_", "1T1_0_", "-1T1_0_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # T-junction left turn
        configs["t-left"] = ScenarioMetaDriveConfig(
            scenario_name="t-left",
            maneuver="t_junction_left",
            map_name="T",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(50.0, 60.0),
                lane_index="-1T0_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.15,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1T0_0_", "1T1_0_", "-1T1_0_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # T-junction right turn
        configs["t-right"] = ScenarioMetaDriveConfig(
            scenario_name="t-right",
            maneuver="t_junction_right",
            map_name="T",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 3.5),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(50.0, -30.0),
                lane_index="1T0_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.15,
                vehicle_types=["car", "two_wheeler", "auto_rickshaw"],
                spawn_lanes=["-1T0_0_", "1T1_0_", "-1T1_0_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=True,
                density=0.05,
                crossing_zones=[(45, 4, 55, 10), (45, -3, 55, 3)]
            )
        )

        # ============================================================
        # Y-JUNCTION SCENARIOS (Y map)
        # ============================================================

        # Y-junction - vehicle on stem, choose branch
        configs["y-junction"] = ScenarioMetaDriveConfig(
            scenario_name="y-junction",
            maneuver="y_junction",
            map_name="Y",
            traffic_density=0.15,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(80.0, 30.0),  # Left branch
                lane_index="1Y1_2_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=True,
                density=0.1,
                vehicle_types=["car", "two_wheeler"],
                spawn_lanes=["-1Y0_0_", "-1Y1_1_", "-1Y1_2_"]
            ),
            pedestrians=PedestrianConfig(
                enabled=False,
                density=0.0
            )
        )

        # Y-junction left branch
        configs["y-left"] = ScenarioMetaDriveConfig(
            scenario_name="y-left",
            maneuver="y_branch_left",
            map_name="Y",
            traffic_density=0.1,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(80.0, 30.0),
                lane_index="1Y1_2_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=False,
                density=0.0
            ),
            pedestrians=PedestrianConfig(enabled=False, density=0.0)
        )

        # Y-junction right branch
        configs["y-right"] = ScenarioMetaDriveConfig(
            scenario_name="y-right",
            maneuver="y_branch_right",
            map_name="Y",
            traffic_density=0.1,
            vehicle_spawn=VehicleSpawnConfig(
                position=(20.0, 7.0),
                heading=0.0,
                lane_index=">>>"
            ),
            destination=DestinationConfig(
                position=(80.0, -10.0),
                lane_index="1Y1_1_"
            ),
            traffic_lights=[
                TrafficLightConfig(position=(50.0, 7.0), initial_state="green")
            ],
            cross_traffic=CrossTrafficConfig(
                enabled=False,
                density=0.0
            ),
            pedestrians=PedestrianConfig(enabled=False, density=0.0)
        )

        return configs

    def get_config(self, scenario_name: str) -> ScenarioMetaDriveConfig:
        """Get MetaDrive configuration for a scenario."""
        scenario_name = scenario_name.strip().lower().replace("_", "-")

        if scenario_name not in self._configs:
            print(f"Warning: Unknown scenario '{scenario_name}', using 'straight'")
            scenario_name = "straight"

        return self._configs[scenario_name]

    def get_map_name(self, scenario_name: str) -> str:
        """Get physical MetaDrive map name for scenario."""
        config = self.get_config(scenario_name)
        return config.map_name

    def get_scenario_list(self) -> List[str]:
        """Get list of all available scenario names."""
        return list(self._configs.keys())

    def print_config(self, scenario_name: str):
        """Print configuration for a scenario."""
        config = self.get_config(scenario_name)
        print(f"\n{'='*60}")
        print(f"SCENARIO CONFIG: {config.scenario_name}")
        print(f"{'='*60}")
        print(f"Map: {config.map_name}")
        print(f"Maneuver: {config.maneuver}")
        print(f"Traffic Density: {config.traffic_density}")
        print(f"\nVehicle Spawn:")
        print(f"  Position: {config.vehicle_spawn.position}")
        print(f"  Heading: {config.vehicle_spawn.heading:.2f} rad ({np.degrees(config.vehicle_spawn.heading):.1f} deg)")
        print(f"  Lane: {config.vehicle_spawn.lane_index}")
        print(f"\nDestination:")
        print(f"  Position: {config.destination.position}")
        print(f"  Lane: {config.destination.lane_index}")
        print(f"\nTraffic Lights: {len(config.traffic_lights)}")
        for i, tl in enumerate(config.traffic_lights):
            print(f"  {i+1}. Position: {tl.position}, State: {tl.initial_state}")
        print(f"\nCross Traffic:")
        print(f"  Enabled: {config.cross_traffic.enabled}")
        print(f"  Density: {config.cross_traffic.density}")
        print(f"  Vehicle Types: {config.cross_traffic.vehicle_types}")
        print(f"  Spawn Lanes: {config.cross_traffic.spawn_lanes}")
        print(f"\nPedestrians:")
        print(f"  Enabled: {config.pedestrians.enabled}")
        print(f"  Density: {config.pedestrians.density}")
        print(f"  Crossing Zones: {len(config.pedestrians.crossing_zones)}")
        print(f"{'='*60}\n")


# Convenience function
def create_scenario_configurator() -> ScenarioConfigurator:
    """Create and return a ScenarioConfigurator instance."""
    return ScenarioConfigurator()


if __name__ == "__main__":
    # Test the configurator
    configurator = create_scenario_configurator()

    print("Available scenarios:")
    for s in configurator.get_scenario_list():
        print(f"  - {s}")

    print("\n" + "="*60)

    # Print config for each scenario type
    for scenario in ["straight", "left-turn", "right-turn", "yield", "stop-and-go",
                     "t-junction", "t-left", "t-right", "y-junction", "y-left", "y-right"]:
        configurator.print_config(scenario)