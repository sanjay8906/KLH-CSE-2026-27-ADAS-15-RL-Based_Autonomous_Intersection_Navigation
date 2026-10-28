import argparse
import json

from metadrive.manager.traffic_manager import TrafficMode

from adas_sim.metadrive.adapter import MetaDriveSimulator

from adas_sim.sensors.lidar import LidarSensor
from adas_sim.sensors.camera import CameraSensor
from adas_sim.sensors.vehicle_state import VehicleState

from adas_sim.controllers.vehicle_controller import VehicleController

from adas_sim.sensors.radar import RadarSensor
from adas_sim.sensors.ultrasonic import UltrasonicSensor
from adas_sim.sensors.gps import GPSSensor
from adas_sim.sensors.imu import IMUSensor

from adas_sim.sensors.sensor_fusion import SensorFusion, create_sensor_fusion, FusedPerception

from adas_sim.gui.sensor_display import SensorDisplay


# ============================================================
# MAP VALUE NORMALIZATION
# ============================================================

def normalize_map_value(value):
    """
    Convert numeric map values supplied as strings into integers.

    Example:
        "3" -> 3
        "X" -> "X"
    """
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return value
    return value


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="ADAS Intersection Driving Simulation"
    )

    # ========================================================
    # ENVIRONMENT
    # ========================================================

    parser.add_argument(
        "--traffic-density",
        type=float,
        default=None,  # Will use scenario default
        help="Traffic density from 0.0 to 1.0 (overrides scenario default)"
    )

    parser.add_argument(
        "--weather",
        type=str,
        default=None,
        help="Weather condition"
    )

    parser.add_argument(
        "--night",
        action="store_true",
        help="Enable night mode"
    )

    parser.add_argument(
        "--map",
        type=str,
        default="3",
        help="MetaDrive map index (overridden by scenario)"
    )

    # ========================================================
    # INTERSECTION SCENARIOS
    # ========================================================

    parser.add_argument(
        "--scenario",
        type=str,
        default="straight",
        choices=[
            # 4-way intersection
            "straight",
            "left-turn",
            "right-turn",
            "yield",
            "stop-and-go",

            # T-junction
            "t-junction",
            "t-left",
            "t-right",

            # Y-junction
            "y-junction",
            "y-left",
            "y-right",
        ],
        help="Intersection scenario"
    )

    # ========================================================
    # RANDOMIZATION
    # ========================================================

    parser.add_argument(
        "--random-lane-width",
        action="store_true",
        help="Randomize lane width"
    )

    parser.add_argument(
        "--random-lane-num",
        action="store_true",
        help="Randomize number of lanes"
    )

    # ========================================================
    # TRAFFIC MODE
    # ========================================================

    parser.add_argument(
        "--traffic-mode",
        type=str,
        choices=[
            "Trigger",
            "Random",
            "None"
        ],
        default="Trigger",
        help="Traffic mode"
    )

    # ========================================================
    # MANUAL MODE
    # ========================================================

    parser.add_argument(
        "--manual",
        action="store_true",
        help="Start in manual mode"
    )

    # ========================================================
    # SENSOR FUSION
    # ========================================================

    parser.add_argument(
        "--fusion-fov",
        type=float,
        default=180.0,
        help="Sensor fusion field of view in degrees"
    )

    parser.add_argument(
        "--fusion-range",
        type=float,
        default=50.0,
        help="Sensor fusion maximum range in meters"
    )

    # ========================================================
    # ADDITIONAL CONFIG
    # ========================================================

    parser.add_argument(
        "--config",
        type=str,
        help="Additional environment configuration as JSON"
    )

    args = parser.parse_args()

    # ========================================================
    # BUILD ENVIRONMENT CONFIGURATION
    # ========================================================

    env_config = {
        "map": normalize_map_value(args.map),
        "traffic_density": args.traffic_density,
        "num_scenarios": 1,
        "use_render": True,
        "manual_control": False,
        "image_observation": False,
    }

    # ========================================================
    # WEATHER
    # ========================================================

    if args.weather is not None:
        env_config["weather"] = args.weather

    # ========================================================
    # NIGHT MODE
    # ========================================================

    if args.night:
        env_config["night"] = True

    # ========================================================
    # RANDOM LANE WIDTH
    # ========================================================

    if args.random_lane_width:
        env_config["random_lane_width"] = True

    # ========================================================
    # RANDOM LANE NUMBER
    # ========================================================

    if args.random_lane_num:
        env_config["random_lane_num"] = True

    # ========================================================
    # TRAFFIC MODE
    # ========================================================

    if args.traffic_mode is not None:
        if args.traffic_mode == "None":
            env_config["traffic_mode"] = None
        else:
            env_config["traffic_mode"] = getattr(
                TrafficMode,
                args.traffic_mode
            )

    # ========================================================
    # ADDITIONAL JSON CONFIG
    # ========================================================

    if args.config:
        try:
            extra_config = json.loads(args.config)
            for key, value in extra_config.items():
                if key == "map":
                    env_config[key] = normalize_map_value(value)
                else:
                    env_config[key] = value
        except json.JSONDecodeError:
            print("WARNING: Could not parse JSON config:")
            print(args.config)

    # ========================================================
    # DISPLAY CONFIGURATION
    # ========================================================

    print()
    print("=" * 70)
    print("       ADAS INTERSECTION DRIVING SIMULATION")
    print("=" * 70)
    print(f"Map              : {env_config['map']}")
    print(f"Scenario         : {args.scenario}")
    print(f"Traffic Density  : {env_config.get('traffic_density', 'scenario default')}")
    print(f"Manual Mode      : {args.manual}")
    print(f"Fusion FOV       : {args.fusion_fov}°")
    print(f"Fusion Range     : {args.fusion_range}m")
    print("=" * 70)
    print()

    # ========================================================
    # OBJECT REFERENCES
    # ========================================================

    simulator = None
    display = None

    try:
        # ====================================================
        # CREATE SIMULATOR
        # ====================================================

        simulator = MetaDriveSimulator(
            render=True,
            manual=False,
            scenario=args.scenario,
            **env_config
        )

        # ====================================================
        # CREATE SENSORS
        # ====================================================

        print()
        print("Initializing sensors...")

        lidar = LidarSensor(num_lasers=240)
        camera = CameraSensor()
        vehicle_state = VehicleState()
        radar = RadarSensor()
        ultrasonic = UltrasonicSensor()
        gps = GPSSensor()
        imu = IMUSensor()

        # ====================================================
        # CREATE SENSOR FUSION
        # ====================================================

        print("Initializing sensor fusion...")
        sensor_fusion = create_sensor_fusion(
            lidar=lidar,
            radar=radar,
            ultrasonic=ultrasonic,
            camera=camera,
            gps=gps,
            imu=imu,
            vehicle_state=vehicle_state,
            max_range=args.fusion_range,
            fusion_fov_deg=args.fusion_fov
        )

        # ====================================================
        # SENSOR DISPLAY
        # ====================================================

        display = SensorDisplay()

        # ====================================================
        # RESET ENVIRONMENT
        # ====================================================

        print()
        print("Starting MetaDrive...")

        observation, info = simulator.reset()

        # ====================================================
        # VEHICLE CONTROLLER
        # ====================================================

        controller = VehicleController(manual=args.manual)

        # ====================================================
        # M = MANUAL / AUTO
        # ====================================================

        simulator.env.engine.accept("m", controller.toggle)

        # ====================================================
        # SCENARIO INFORMATION
        # ====================================================

        print()
        print("Intersection scenario:")
        print(simulator.get_scenario_summary())

        # ====================================================
        # CONTROLS
        # ====================================================

        print()
        print("=" * 70)
        print("CONTROLS")
        print("=" * 70)
        print("W / UP       -> Accelerate")
        print("S / DOWN     -> Reverse")
        print("A / LEFT     -> Turn LEFT")
        print("D / RIGHT    -> Turn RIGHT")
        print("M            -> Toggle MANUAL / AUTO")
        print("1-9          -> Switch scenario (1=straight, 2=left-turn, etc.)")
        print("R            -> Reset current scenario")
        print("ESC          -> Close simulator")
        print("=" * 70)
        print()

        # ====================================================
        # MAIN LOOP
        # ====================================================

        step_count = 0
        scenario_keys = {
            "1": "straight",
            "2": "left-turn",
            "3": "right-turn",
            "4": "yield",
            "5": "stop-and-go",
            "6": "t-junction",
            "7": "t-left",
            "8": "t-right",
            "9": "y-junction",
        }

        def switch_scenario(new_scenario):
            nonlocal simulator, sensor_fusion, controller, observation, info, step_count
            print(f"\nSwitching to scenario: {new_scenario}")
            simulator.close()
            sensor_fusion.reset()
            simulator = MetaDriveSimulator(
                render=True,
                manual=controller.manual,
                scenario=new_scenario,
                **env_config
            )
            observation, info = simulator.reset()
            step_count = 0
            print(f"Switched to {new_scenario}")

        # Register scenario switch keys
        for key, scenario_name in scenario_keys.items():
            simulator.env.engine.accept(key, lambda s=scenario_name: switch_scenario(s))

        # Reset key
        simulator.env.engine.accept("r", lambda: switch_scenario(args.scenario))

        while True:
            # =================================================
            # CURRENT VEHICLE
            # =================================================

            vehicle = simulator.get_vehicle()

            if vehicle is None:
                print("ERROR: Vehicle is None.")
                break

            # =================================================
            # INTERSECTION INFORMATION
            # =================================================

            intersection_info = simulator.get_intersection_info(vehicle.position)

            # =================================================
            # SENSOR FUSION
            # =================================================

            scenario_config = simulator.get_scenario_config()
            fused_perception: FusedPerception = sensor_fusion.process(
                observation,
                vehicle,
                scenario_config=scenario_config
            )

            # =================================================
            # SELECT ACTION
            # =================================================

            if controller.manual:
                action = controller.manual_drive()
            else:
                # Use fused perception for auto driving
                action = controller.auto_drive(
                    vehicle,
                    fused_perception.objects,
                    fused_perception
                )

            # =================================================
            # STEP METADRIVE
            # =================================================

            observation, reward, terminated, truncated, info = simulator.step(action)

            # =================================================
            # CAMERA
            # =================================================

            camera_image = simulator.get_camera_image()

            # =================================================
            # SENSOR GUI
            # =================================================

            if display is not None:
                try:
                    # Update display with fused perception data
                    display.update(
                        camera_image,
                        fused_perception,
                        simulator.get_scenario_summary()
                    )
                except Exception as e:
                    print("GUI update error:", e)

            # =================================================
            # STEP COUNTER
            # =================================================

            step_count += 1

            # =================================================
            # STATUS
            # =================================================

            if step_count % 20 == 0:
                maneuver = intersection_info.get("maneuver", "unknown")
                speed = fused_perception.ego_speed
                heading = fused_perception.ego_heading
                num_objects = len(fused_perception.objects)
                closest_obj = fused_perception.get_closest_object(30.0)
                closest_dist = closest_obj.distance() if closest_obj else float('inf')

                print(
                    f"Step: {step_count}"
                    f" | Mode: {'MANUAL' if controller.manual else 'AUTO'}"
                    f" | Steering: {action[0]:.2f}"
                    f" | Throttle: {action[1]:.2f}"
                    f" | Speed: {speed:.2f}"
                    f" | Heading: {heading:.2f}"
                    f" | Objects: {num_objects}"
                    f" | Closest: {closest_dist:.1f}m"
                    f" | Scenario: {maneuver}"
                )

            # =================================================
            # EPISODE END
            # =================================================

            if terminated or truncated:
                print()
                print("=" * 60)
                print(f"Episode ended after {step_count} steps")
                print("=" * 60)

                # Reset sensors
                sensor_fusion.reset()

                # Reset MetaDrive
                observation, info = simulator.reset()
                step_count = 0

    # ========================================================
    # KEYBOARD INTERRUPT
    # ========================================================

    except KeyboardInterrupt:
        print()
        print("Simulation stopped by user.")

    # ========================================================
    # ERROR
    # ========================================================

    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR IN ADAS SIMULATION")
        print("=" * 70)
        print(f"{type(e).__name__}: {e}")
        raise

    # ========================================================
    # CLEANUP
    # ========================================================

    finally:
        print()
        print("Closing ADAS simulation...")

        if display is not None:
            try:
                display.close()
            except Exception:
                pass

        if simulator is not None:
            try:
                simulator.close()
            except Exception:
                pass

        print("Simulation closed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()