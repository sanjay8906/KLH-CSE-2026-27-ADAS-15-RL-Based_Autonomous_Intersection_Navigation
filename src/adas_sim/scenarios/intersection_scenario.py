from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class IntersectionScenario:

    # Scenario identification
    name: str
    maneuver: str

    # Road geometry
    road_type: str = "4-way"

    # Directions
    incoming_lanes: tuple[str, ...] = field(
        default_factory=lambda: ("north", "south", "east", "west")
    )

    outgoing_lanes: tuple[str, ...] = field(
        default_factory=lambda: ("north", "south", "east", "west")
    )

    # Traffic control
    traffic_light_state: str = "green"
    yield_to_cross_traffic: bool = False

    # Driving parameters
    speed_limit: float = 25.0
    stop_distance: float = 12.0

    # Extra ADAS scenario information
    cross_traffic: bool = True
    pedestrian_crossing: bool = False
    emergency_braking: bool = True

    def to_dict(self) -> dict:

        return {
            "name": self.name,
            "maneuver": self.maneuver,

            # Road geometry
            "road_type": self.road_type,
            "is_intersection": True,

            # Lanes
            "incoming_lanes": list(self.incoming_lanes),
            "outgoing_lanes": list(self.outgoing_lanes),

            # Traffic
            "traffic_light_state": self.traffic_light_state,
            "yield_to_cross_traffic": self.yield_to_cross_traffic,
            "cross_traffic": self.cross_traffic,

            # Safety
            "pedestrian_crossing": self.pedestrian_crossing,
            "emergency_braking": self.emergency_braking,

            # Driving
            "speed_limit": self.speed_limit,
            "stop_distance": self.stop_distance,
        }


# ============================================================
# INTERSECTION SCENARIOS
# ============================================================

INTERSECTION_SCENARIOS = {

    # --------------------------------------------------------
    # 1. FOUR-WAY CROSS - STRAIGHT
    # --------------------------------------------------------

    "straight": IntersectionScenario(
        name="straight",
        maneuver="go_straight",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        traffic_light_state="green",
        yield_to_cross_traffic=False,

        speed_limit=25.0,
        stop_distance=8.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 2. FOUR-WAY CROSS - LEFT TURN
    # --------------------------------------------------------

    "left-turn": IntersectionScenario(
        name="left-turn",
        maneuver="turn_left",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        traffic_light_state="green",
        yield_to_cross_traffic=True,

        speed_limit=20.0,
        stop_distance=10.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 3. FOUR-WAY CROSS - RIGHT TURN
    # --------------------------------------------------------

    "right-turn": IntersectionScenario(
        name="right-turn",
        maneuver="turn_right",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        traffic_light_state="green",
        yield_to_cross_traffic=True,

        speed_limit=20.0,
        stop_distance=6.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 4. FOUR-WAY CROSS - YIELD
    # --------------------------------------------------------

    "yield": IntersectionScenario(
        name="yield",
        maneuver="yield_to_cross_traffic",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        traffic_light_state="yellow",
        yield_to_cross_traffic=True,

        speed_limit=15.0,
        stop_distance=9.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 5. FOUR-WAY CROSS - STOP AND GO
    # --------------------------------------------------------

    "stop-and-go": IntersectionScenario(
        name="stop-and-go",
        maneuver="stop_and_go",

        road_type="4-way",

        incoming_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "south",
            "east",
            "west"
        ),

        traffic_light_state="red",
        yield_to_cross_traffic=True,

        speed_limit=10.0,
        stop_distance=12.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 6. T-JUNCTION
    # --------------------------------------------------------

    "t-junction": IntersectionScenario(
        name="t-junction",
        maneuver="t_junction",

        road_type="T",

        # Example:
        # Vehicle comes from south.
        # Road branches east/west.
        incoming_lanes=(
            "south",
            "east",
            "west"
        ),

        outgoing_lanes=(
            "north",
            "east",
            "west"
        ),

        traffic_light_state="green",
        yield_to_cross_traffic=True,

        speed_limit=20.0,
        stop_distance=10.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 7. Y-JUNCTION
    # --------------------------------------------------------

    "y-junction": IntersectionScenario(
        name="y-junction",
        maneuver="y_junction",

        road_type="Y",

        # One incoming road splits into two branches.
        incoming_lanes=(
            "south",
        ),

        outgoing_lanes=(
            "north-east",
            "north-west"
        ),

        traffic_light_state="green",
        yield_to_cross_traffic=True,

        speed_limit=20.0,
        stop_distance=8.0,

        cross_traffic=True,
        pedestrian_crossing=False,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 8. T-JUNCTION LEFT
    # --------------------------------------------------------

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

        speed_limit=15.0,
        stop_distance=8.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 9. T-JUNCTION RIGHT
    # --------------------------------------------------------

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

        speed_limit=15.0,
        stop_distance=8.0,

        cross_traffic=True,
        pedestrian_crossing=True,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 10. Y-JUNCTION LEFT
    # --------------------------------------------------------

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

        speed_limit=15.0,
        stop_distance=7.0,

        cross_traffic=False,
        pedestrian_crossing=False,
        emergency_braking=True,
    ),

    # --------------------------------------------------------
    # 11. Y-JUNCTION RIGHT
    # --------------------------------------------------------

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

        speed_limit=15.0,
        stop_distance=7.0,

        cross_traffic=False,
        pedestrian_crossing=False,
        emergency_braking=True,
    ),
}


# ============================================================
# SCENARIO CREATOR
# ============================================================

def create_intersection_scenario(
    name: str | None = None
) -> IntersectionScenario:

    scenario_name = (
        name or "straight"
    ).strip().lower().replace("_", "-")

    scenario = INTERSECTION_SCENARIOS.get(
        scenario_name
    )

    if scenario is not None:
        return scenario

    print(
        f"Unknown scenario '{name}'. "
        f"Using 'straight'."
    )

    return INTERSECTION_SCENARIOS["straight"]