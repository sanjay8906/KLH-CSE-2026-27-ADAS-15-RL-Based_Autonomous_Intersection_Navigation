from __future__ import annotations

from dataclasses import dataclass, field


# ============================================================
# INTERSECTION SCENARIO (Legacy - kept for backwards compatibility)
# ============================================================

@dataclass(frozen=True)
class IntersectionScenario:

    # Basic information
    name: str
    maneuver: str

    # Physical road classification
    # 4-way = Cross intersection
    # T     = T junction
    # Y     = Y junction
    road_type: str = "4-way"

    # Incoming and outgoing directions
    incoming_lanes: tuple[str, ...] = field(
        default_factory=lambda: (
            "north",
            "south",
            "east",
            "west",
        )
    )

    outgoing_lanes: tuple[str, ...] = field(
        default_factory=lambda: (
            "north",
            "south",
            "east",
            "west",
        )
    )

    # Traffic conditions
    traffic_light_state: str = "green"
    yield_to_cross_traffic: bool = False
    cross_traffic: bool = True

    # ADAS parameters
    speed_limit: float = 25.0
    stop_distance: float = 12.0

    # Additional scenario conditions
    pedestrian_crossing: bool = False
    emergency_braking: bool = True

    # ========================================================
    # CONVERT TO DICTIONARY
    # ========================================================

    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "maneuver": self.maneuver,

            "road_type": self.road_type,
            "is_intersection": True,

            "incoming_lanes": list(
                self.incoming_lanes
            ),

            "outgoing_lanes": list(
                self.outgoing_lanes
            ),

            "traffic_light_state":
                self.traffic_light_state,

            "yield_to_cross_traffic":
                self.yield_to_cross_traffic,

            "cross_traffic":
                self.cross_traffic,

            "speed_limit":
                self.speed_limit,

            "stop_distance":
                self.stop_distance,

            "pedestrian_crossing":
                self.pedestrian_crossing,

            "emergency_braking":
                self.emergency_braking,
        }


# ============================================================
# LEGACY SCENARIOS (kept for backwards compatibility)
# ============================================================

INTERSECTION_SCENARIOS = {

    # ========================================================
    # 4-WAY CROSS INTERSECTION
    # ========================================================

    "straight": IntersectionScenario(

        name="straight",

        maneuver="go_straight",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=False,

        cross_traffic=True,

        speed_limit=25.0,

        stop_distance=8.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # 4-WAY LEFT TURN
    # ========================================================

    "left-turn": IntersectionScenario(

        name="left-turn",

        maneuver="turn_left",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=20.0,

        stop_distance=10.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # 4-WAY RIGHT TURN
    # ========================================================

    "right-turn": IntersectionScenario(

        name="right-turn",

        maneuver="turn_right",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=20.0,

        stop_distance=6.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # 4-WAY YIELD
    # ========================================================

    "yield": IntersectionScenario(

        name="yield",

        maneuver="yield_to_cross_traffic",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        traffic_light_state="yellow",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=15.0,

        stop_distance=9.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # 4-WAY STOP AND GO
    # ========================================================

    "stop-and-go": IntersectionScenario(

        name="stop-and-go",

        maneuver="stop_and_go",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west",
        ),

        traffic_light_state="red",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=10.0,

        stop_distance=12.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # T-JUNCTION
    # ========================================================

    "t-junction": IntersectionScenario(

        name="t-junction",

        maneuver="t_junction",

        road_type="T",

        incoming_lanes=(
            "south",
            "east",
            "west",
        ),

        outgoing_lanes=(
            "east",
            "west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=20.0,

        stop_distance=10.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # T-JUNCTION LEFT
    # ========================================================

    "t-left": IntersectionScenario(

        name="t-left",

        maneuver="t_junction_left",

        road_type="T",

        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=15.0,

        stop_distance=8.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # T-JUNCTION RIGHT
    # ========================================================

    "t-right": IntersectionScenario(

        name="t-right",

        maneuver="t_junction_right",

        road_type="T",

        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "east",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=15.0,

        stop_distance=8.0,

        pedestrian_crossing=True,

        emergency_braking=True,
    ),

    # ========================================================
    # Y-JUNCTION
    # ========================================================

    "y-junction": IntersectionScenario(

        name="y-junction",

        maneuver="y_junction",

        road_type="Y",

        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "north-west",
            "north-east",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=True,

        speed_limit=20.0,

        stop_distance=8.0,

        pedestrian_crossing=False,

        emergency_braking=True,
    ),

    # ========================================================
    # Y-JUNCTION LEFT
    # ========================================================

    "y-left": IntersectionScenario(

        name="y-left",

        maneuver="y_branch_left",

        road_type="Y",

        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "north-west",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=False,

        speed_limit=15.0,

        stop_distance=7.0,

        pedestrian_crossing=False,

        emergency_braking=True,
    ),

    # ========================================================
    # Y-JUNCTION RIGHT
    # ========================================================

    "y-right": IntersectionScenario(

        name="y-right",

        maneuver="y_branch_right",

        road_type="Y",

        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "north-east",
        ),

        traffic_light_state="green",

        yield_to_cross_traffic=True,

        cross_traffic=False,

        speed_limit=15.0,

        stop_distance=7.0,

        pedestrian_crossing=False,

        emergency_braking=True,
    ),
}


# ============================================================
# SCENARIO FACTORY
# ============================================================

def create_intersection_scenario(
    name: str | None = None
) -> IntersectionScenario:

    scenario_name = (
        name or "straight"
    ).strip().lower().replace("_", "-")

    if scenario_name in INTERSECTION_SCENARIOS:

        return INTERSECTION_SCENARIOS[
            scenario_name
        ]

    print(
        f"WARNING: Unknown scenario '{name}'."
    )

    print(
        "Using default scenario: straight"
    )

    return INTERSECTION_SCENARIOS[
        "straight"
    ]


# ============================================================
# NEW SCENARIO CONFIGURATOR (for MetaDrive integration)
# ============================================================

from .scenario_configurator import (
    ScenarioConfigurator,
    create_scenario_configurator,
    ScenarioMetaDriveConfig,
    VehicleSpawnConfig,
    DestinationConfig,
    TrafficLightConfig,
    CrossTrafficConfig,
    PedestrianConfig
)

__all__ = [
    "IntersectionScenario",
    "INTERSECTION_SCENARIOS",
    "create_intersection_scenario",
    "ScenarioConfigurator",
    "create_scenario_configurator",
    "ScenarioMetaDriveConfig",
    "VehicleSpawnConfig",
    "DestinationConfig",
    "TrafficLightConfig",
    "CrossTrafficConfig",
    "PedestrianConfig",
]