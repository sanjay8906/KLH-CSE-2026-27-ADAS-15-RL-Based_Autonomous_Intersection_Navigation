from adas_sim.metadrive.adapter import MetaDriveSimulator
from adas_sim.controllers.vehicle_controller import VehicleController
import time

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

    observation, info = simulator.reset()
    print("MetaDrive started successfully.")

    controller = VehicleController(manual=True)
    simulator.env.engine.accept("m", controller.toggle)

    # Run for a few steps
    for i in range(100):
        action = controller.manual_drive()
        observation, reward, terminated, truncated, info = simulator.step(action)

        if terminated or truncated:
            print(f"Episode ended at step {i}. Resetting...")
            observation, info = simulator.reset()

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopped by user.")
except Exception as e:
    print(f"\nError: {repr(e)}")
    import traceback
    traceback.print_exc()
finally:
    if simulator is not None:
        try:
            simulator.close()
        except Exception:
            pass
    print("Done.")