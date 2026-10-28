import numpy as np
from direct.controls.InputState import InputState

from adas_sim.sensors.sensor_fusion import FusedPerception, FusedObject, ObjectClass


class VehicleController:
    """
    Vehicle controller with manual and automatic driving modes.

    Auto mode is now intersection-aware using fused sensor perception.
    """

    def __init__(self, manual=False):
        self.manual = bool(manual)
        self.steering = 0.0
        self.throttle = 0.0

        # ============================================================
        # KEYBOARD
        # ============================================================

        self.inputs = InputState()

        self.inputs.watchWithModifiers("left", "a")
        self.inputs.watchWithModifiers("right", "d")
        self.inputs.watchWithModifiers("forward", "w")
        self.inputs.watchWithModifiers("reverse", "s")
        self.inputs.watchWithModifiers("left_arrow", "arrow_left")
        self.inputs.watchWithModifiers("right_arrow", "arrow_right")
        self.inputs.watchWithModifiers("up_arrow", "arrow_up")
        self.inputs.watchWithModifiers("down_arrow", "arrow_down")

        print("Vehicle Controller Initialized")

    # ================================================================
    # MODE
    # ================================================================

    def set_mode(self, manual):
        self.manual = bool(manual)
        print("Mode:", "MANUAL" if self.manual else "AUTO")

    def toggle(self):
        self.manual = not self.manual
        print("Mode:", "MANUAL" if self.manual else "AUTO")

    # ================================================================
    # MANUAL CONTROL
    # ================================================================

    def manual_drive(self):
        steering = 0.0
        throttle = 0.0

        # ============================================================
        # LEFT
        # ============================================================
        if self.inputs.isSet("left") or self.inputs.isSet("left_arrow"):
            steering = -1.0

        # ============================================================
        # RIGHT
        # ============================================================
        elif self.inputs.isSet("right") or self.inputs.isSet("right_arrow"):
            steering = 1.0

        # ============================================================
        # FORWARD
        # ============================================================
        if self.inputs.isSet("forward") or self.inputs.isSet("up_arrow"):
            throttle = 0.35

        # ============================================================
        # REVERSE
        # ============================================================
        elif self.inputs.isSet("reverse") or self.inputs.isSet("down_arrow"):
            throttle = -0.35

        # ============================================================
        # STOP
        # ============================================================
        else:
            throttle = 0.0

        # ============================================================
        # LIMIT
        # ============================================================
        self.steering = float(np.clip(steering, -1.0, 1.0))
        self.throttle = float(np.clip(throttle, -1.0, 1.0))

        return [self.steering, self.throttle]

    # ================================================================
    # AUTOMATIC DRIVING - INTERSECTION AWARE
    # ================================================================

    def auto_drive(
        self,
        vehicle,
        fused_objects,
        fused_perception: FusedPerception = None
    ):
        """
        Intersection-aware automatic driving using fused perception.

        Args:
            vehicle: MetaDrive vehicle object
            fused_objects: List of FusedObject from sensor fusion
            fused_perception: Complete FusedPerception (optional)
        """
        # -----------------------------------------------------------
        # Lane following (base behavior)
        # -----------------------------------------------------------
        lane = vehicle.lane
        longitudinal, lateral = lane.local_coordinates(vehicle.position)
        lane_heading = lane.heading_theta_at(longitudinal)

        heading_error = lane_heading - vehicle.heading_theta
        heading_error = np.arctan2(np.sin(heading_error), np.cos(heading_error))

        look_ahead = np.clip(3.0 + vehicle.speed * 0.35, 3.0, 8.0)
        look_distance = min(longitudinal + look_ahead, lane.length - 0.1)
        target_heading = lane.heading_theta_at(look_distance)

        future_heading_error = target_heading - vehicle.heading_theta
        future_heading_error = np.arctan2(np.sin(future_heading_error), np.cos(future_heading_error))

        steering = 1.8 * heading_error + 1.2 * future_heading_error
        steering += -0.20 * lateral

        steering = float(np.clip(steering, -1.0, 1.0))

        # -----------------------------------------------------------
        # Obstacle avoidance using fused perception
        # -----------------------------------------------------------
        speed = float(vehicle.speed)
        steering_amount = abs(steering)

        # Base target throttle based on steering
        if steering_amount > 0.70:
            target_throttle = 0.12
        elif steering_amount > 0.40:
            target_throttle = 0.17
        else:
            target_throttle = 0.25

        # Check for obstacles in front using fused perception
        closest_obj = None
        min_distance = float('inf')

        for obj in fused_objects:
            # Only consider objects in front within reasonable distance
            if obj.distance() < min_distance and obj.distance() < 30.0:
                bearing = abs(obj.bearing())
                if bearing < np.radians(60):  # 60 degree FOV for obstacle avoidance
                    min_distance = obj.distance()
                    closest_obj = obj

        # Obstacle avoidance logic
        if closest_obj is not None:
            dist = closest_obj.distance()
            obj_class = closest_obj.object_class
            rel_speed = closest_obj.relative_speed()

            print(f"[AUTO] Obstacle: {obj_class.name} at {dist:.1f}m, "
                  f"bearing={np.degrees(closest_obj.bearing()):.1f}°, "
                  f"rel_speed={rel_speed:.1f}m/s")

            # Emergency braking for very close objects
            if dist < 3.0:
                throttle = -0.5  # Hard brake
            elif dist < 5.0:
                throttle = 0.0  # Stop
            elif dist < 8.0:
                throttle = min(target_throttle, 0.1)  # Slow down
            elif dist < 15.0:
                throttle = min(target_throttle, 0.15)  # Caution
            else:
                throttle = target_throttle

            # If object is moving towards us (negative relative speed = approaching)
            if closest_obj.velocity[0] < -2.0:  # Object approaching fast
                throttle = min(throttle, 0.05)
        else:
            throttle = target_throttle

        # -----------------------------------------------------------
        # Speed protection
        # -----------------------------------------------------------
        if speed > 14.0:
            throttle = 0.0

        # -----------------------------------------------------------
        # Intersection-specific logic (if perception available)
        # -----------------------------------------------------------
        if fused_perception is not None:
            throttle = self._intersection_logic(
                vehicle, fused_perception, throttle, steering
            )

        return [steering, throttle]

    def _intersection_logic(
        self,
        vehicle,
        perception: FusedPerception,
        throttle: float,
        steering: float
    ) -> float:
        """
        Apply intersection-specific driving logic.

        Handles:
        - Traffic light compliance
        - Yield to cross traffic
        - Stop sign behavior
        - Turn navigation
        """
        # Get intersection info
        intersection_info = perception.intersection_info
        if not intersection_info:
            return throttle

        maneuver = intersection_info.get("maneuver", "unknown")
        # Use the dynamic traffic light state from sensor fusion
        traffic_light = perception.traffic_light_state
        distance_to_intersection = perception.distance_to_intersection

        # If we're far from intersection, no special logic needed
        if distance_to_intersection > 20.0:
            return throttle

        speed = perception.ego_speed

        # -----------------------------------------------------------
        # Traffic light handling
        # -----------------------------------------------------------
        if traffic_light == "red":
            # Stop before intersection
            if distance_to_intersection < 10.0 and speed > 0.5:
                return -0.3  # Brake
            elif distance_to_intersection < 5.0:
                return 0.0  # Full stop
        elif traffic_light == "yellow":
            # Prepare to stop if close
            if distance_to_intersection < 15.0 and speed > 5.0:
                return min(throttle, 0.1)

        # -----------------------------------------------------------
        # Yield scenarios
        # -----------------------------------------------------------
        if intersection_info.get("yield_to_cross_traffic", False):
            # Check for cross traffic using fused objects
            cross_traffic = []
            for obj in perception.objects:
                # Cross traffic would be perpendicular to our heading
                bearing = abs(obj.bearing())
                if np.radians(60) < bearing < np.radians(120):
                    if obj.distance() < 20.0:
                        cross_traffic.append(obj)

            if cross_traffic:
                # Yield to cross traffic
                closest_cross = min(cross_traffic, key=lambda o: o.distance())
                if closest_cross.distance() < 15.0:
                    if speed > 1.0:
                        return -0.2  # Slow down
                    else:
                        return 0.0  # Stop and wait

        # -----------------------------------------------------------
        # Turn-specific speed adjustments
        # -----------------------------------------------------------
        if "left" in maneuver:
            # Left turns need lower speed
            if distance_to_intersection < 15.0 and speed > 8.0:
                return min(throttle, 0.1)
        elif "right" in maneuver:
            # Right turns can be slightly faster
            if distance_to_intersection < 10.0 and speed > 10.0:
                return min(throttle, 0.15)

        return throttle


# ================================================================
# BACKWARDS COMPATIBILITY
# ================================================================

    def auto_drive_legacy(self, vehicle, lidar):
        """Legacy auto_drive for backwards compatibility."""
        # Convert lidar to simple fused objects
        from adas_sim.sensors.sensor_fusion import FusedObject
        objects = []
        if lidar is not None and len(lidar) > 0:
            front_lidar = lidar[:min(30, len(lidar))]
            nearest = float(np.min(front_lidar))
            if nearest < 30.0:
                obj = FusedObject(
                    position=np.array([nearest, 0.0, 0.0]),
                    velocity=np.zeros(3)
                )
                objects.append(obj)
        return self.auto_drive(vehicle, objects, None)