from adas_sim.metadrive.adapter import MetaDriveSimulator
from adas_sim.controllers.vehicle_controller import VehicleController


def main():
    print("=" * 60)
    print("ADAS - MetaDrive Manual Driving")
    print("=" * 60)
    print("Controls:")
    print("  W / UP     -> Accelerate")
    print("  S / DOWN   -> Brake")
    print("  A / LEFT   -> Steer Left")
    print("  D / RIGHT  -> Steer Right")
    print("  M          -> Toggle MANUAL / AUTO")
    print("  ESC        -> Exit")
    print("=" * 60)

    simulator = None

    try:
        simulator = MetaDriveSimulator(
            render=True,
            manual=True,
            scenario="straight",
            traffic_density=0.1,
            num_scenarios=1,
            image_observation=False,
        )

        # Start the environment
        observation, info = simulator.reset()

        print("MetaDrive started successfully.")
        print("Drive the vehicle using W/A/S/D or arrow keys.")
        print("Click the simulator window before using the keyboard.")
        print("Press M to toggle between MANUAL and AUTO mode.")

        # Create vehicle controller for manual input
        controller = VehicleController(manual=True)

        # Bind M key to toggle mode
        simulator.env.engine.accept("m", controller.toggle)

        while True:
            # Get manual action from controller
            action = controller.manual_drive()

            # Step the simulator
            observation, reward, terminated, truncated, info = simulator.step(action)

            if terminated or truncated:
                print("Episode ended. Resetting...")

                observation, info = simulator.reset()

    except KeyboardInterrupt:
        print("\nManual driving stopped by user.")

    except Exception as e:
        print("\nMetaDrive failed to start.")
        print("Error:", repr(e))

    finally:
        if simulator is not None:
            try:
                simulator.close()
            except Exception:
                pass

        print("Simulator closed.")


if __name__ == "__main__":
    main()