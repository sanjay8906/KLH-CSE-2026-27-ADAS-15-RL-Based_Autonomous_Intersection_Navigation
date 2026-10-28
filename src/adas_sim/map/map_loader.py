from adas_sim.scenarios import create_intersection_scenario


class MapLoader:

    def __init__(
        self,
        map_file=None,
        scenario=None
    ):

        print("=" * 60)
        print("ADAS MAP LOADER")
        print("=" * 60)

        self.map_file = map_file

        self.scenario = create_intersection_scenario(
            scenario
        )

        self.map_data = None

        print(
            f"Scenario   : {self.scenario.name}"
        )

        print(
            f"Road Type  : {self.scenario.road_type}"
        )

        print(
            f"Maneuver   : {self.scenario.maneuver}"
        )

        if map_file is not None:

            self.load_map(map_file)

    # ======================================================
    # LOAD MAP
    # ======================================================

    def load_map(self, map_file):

        print(
            f"Loading map: {map_file}"
        )

        self.map_data = {

            "map_file": map_file,

            "intersection": True,

            "road_type":
                self.scenario.road_type,

            "scenario":
                self.scenario.to_dict(),

            "maneuver":
                self.scenario.maneuver,

            "incoming_lanes":
                list(
                    self.scenario.incoming_lanes
                ),

            "outgoing_lanes":
                list(
                    self.scenario.outgoing_lanes
                ),

            "traffic_light":
                self.scenario.traffic_light_state,

            "yield":
                self.scenario.yield_to_cross_traffic,

            "speed_limit":
                self.scenario.speed_limit,

            "stop_distance":
                self.scenario.stop_distance,
        }

        return self.map_data

    # ======================================================
    # ROAD TYPE
    # ======================================================

    def get_road_type(self):

        return self.scenario.road_type

    # ======================================================
    # MANEUVER
    # ======================================================

    def get_maneuver(self):

        return self.scenario.maneuver

    # ======================================================
    # LANE INFORMATION
    # ======================================================

    def get_lane_info(
        self,
        position=None
    ):

        return {

            "lane_id": 0,

            "lane_width": 3.5,

            "curvature": 0.0,

            "speed_limit":
                self.scenario.speed_limit,

            "scenario":
                self.scenario.name,

            "road_type":
                self.scenario.road_type,

            "maneuver":
                self.scenario.maneuver,
        }

    # ======================================================
    # INTERSECTION INFORMATION
    # ======================================================

    def get_intersection_info(
        self,
        position=None
    ):

        info = self.scenario.to_dict()

        # --------------------------------------------------
        # Position
        # --------------------------------------------------

        if position is not None:

            try:

                x = float(position[0])
                y = float(position[1])

            except (
                TypeError,
                IndexError,
                ValueError
            ):

                x = 0.0
                y = 0.0

        else:

            x = 0.0
            y = 0.0

        info["position"] = {
            "x": x,
            "y": y
        }

        # --------------------------------------------------
        # Intersection classification
        # --------------------------------------------------

        info["is_intersection"] = True

        if self.scenario.road_type == "4-way":

            info["intersection_type"] = (
                "four_way"
            )

        elif self.scenario.road_type == "T":

            info["intersection_type"] = (
                "t_junction"
            )

        elif self.scenario.road_type == "Y":

            info["intersection_type"] = (
                "y_junction"
            )

        else:

            info["intersection_type"] = (
                "unknown"
            )

        return info

    # ======================================================
    # SCENARIO CONFIG
    # ======================================================

    def get_scenario_config(self):

        return self.scenario.to_dict()

    # ======================================================
    # PRINT INFORMATION
    # ======================================================

    def print_scenario(self):

        scenario = self.scenario

        print()
        print("=" * 60)
        print("CURRENT SCENARIO")
        print("=" * 60)

        print(
            "Name:",
            scenario.name
        )

        print(
            "Road Type:",
            scenario.road_type
        )

        print(
            "Maneuver:",
            scenario.maneuver
        )

        print(
            "Incoming:",
            scenario.incoming_lanes
        )

        print(
            "Outgoing:",
            scenario.outgoing_lanes
        )

        print(
            "Traffic Light:",
            scenario.traffic_light_state
        )

        print(
            "Yield:",
            scenario.yield_to_cross_traffic
        )

        print(
            "Speed Limit:",
            scenario.speed_limit
        )

        print(
            "Stop Distance:",
            scenario.stop_distance
        )

        print("" + "=" * 60)
        