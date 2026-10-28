try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("Warning: OpenCV not installed. Sensor display will be limited to console output.")

import numpy as np

from adas_sim.sensors.sensor_fusion import FusedPerception, FusedObject, ObjectClass


class SensorDisplay:
    def __init__(self):
        print("Sensor Display Initialized")
        if OPENCV_AVAILABLE:
            # Create windows
            cv2.namedWindow("Camera Feed", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("LiDAR Scan", cv2.WINDOW_AUTOSIZE)
            cv2.namedWindow("Fused Perception", cv2.WINDOW_AUTOSIZE)
            # For LiDAR visualization
            self.lidar_img_width = 400
            self.lidar_img_height = 200
            self.lidar_img = np.zeros((self.lidar_img_height, self.lidar_img_width, 3), dtype=np.uint8)
            # For fused perception bird's eye view
            self.bev_width = 400
            self.bev_height = 400
            self.bev_img = np.zeros((self.bev_height, self.bev_width, 3), dtype=np.uint8)
            self.bev_range = 50.0  # meters
        else:
            self.last_data = None

    def update(self, camera_image, fused_perception: FusedPerception, scenario_info: dict = None):
        """
        Update the display with new sensor data.

        :param camera_image: RGB image from camera (numpy array, HxWx3)
        :param fused_perception: FusedPerception object with all fused data
        :param scenario_info: Scenario information dict
        """
        if OPENCV_AVAILABLE:
            # --- Camera Feed ---
            if camera_image is not None:
                max_width = 800
                h, w = camera_image.shape[:2]
                if w > max_width:
                    scale = max_width / w
                    new_h = int(h * scale)
                    camera_display = cv2.resize(camera_image, (max_width, new_h))
                else:
                    camera_display = camera_image.copy()

                # Overlay text with key sensor info
                ego_speed = fused_perception.ego_speed
                ego_heading = fused_perception.ego_heading
                num_objects = len(fused_perception.objects)

                text_lines = [
                    f"Speed: {ego_speed:.1f} m/s ({ego_speed*3.6:.1f} km/h)",
                    f"Heading: {np.degrees(ego_heading):.1f} deg",
                    f"GPS: ({fused_perception.ego_position[0]:.1f}, {fused_perception.ego_position[1]:.1f})",
                    f"Fused Objects: {num_objects}",
                    f"Sensor Status: {sum(fused_perception.sensor_status.values())}/{len(fused_perception.sensor_status)} active",
                ]

                if scenario_info:
                    maneuver = scenario_info.get("maneuver", "unknown")
                    road_type = scenario_info.get("road_type", "unknown")
                    text_lines.append(f"Scenario: {maneuver} ({road_type})")

                for i, line in enumerate(text_lines):
                    y = 20 + i * 20
                    cv2.putText(camera_display, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                cv2.imshow("Camera Feed", camera_display)

            # --- LiDAR Scan Visualization ---
            # Note: We don't have raw LiDAR directly in fused_perception
            # This would need to be passed separately or reconstructed
            # For now, show a placeholder
            self.lidar_img[:] = 0
            cv2.putText(self.lidar_img, "Raw LiDAR data not in fused_perception",
                       (10, self.lidar_img_height//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(self.lidar_img, "Use fused_perception.objects for obstacles",
                       (10, self.lidar_img_height//2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.imshow("LiDAR Scan", self.lidar_img)

            # --- Bird's Eye View (Fused Perception) ---
            self._draw_bev(fused_perception, scenario_info)
            cv2.imshow("Fused Perception", self.bev_img)

            cv2.waitKey(1)
        else:
            # Fallback: print sensor data to console occasionally
            if self.last_data is None:
                self.last_data = 0
            self.last_data += 1
            if self.last_data % 30 == 0:
                print("\n--- Fused Perception ---")
                print(f"Ego: pos=({fused_perception.ego_position[0]:.1f}, {fused_perception.ego_position[1]:.1f}) "
                      f"speed={fused_perception.ego_speed:.1f} heading={np.degrees(fused_perception.ego_heading):.1f}")
                print(f"Objects: {len(fused_perception.objects)}")
                for i, obj in enumerate(fused_perception.objects[:5]):
                    print(f"  {i}: {obj.object_class.name} dist={obj.distance():.1f}m "
                          f"bearing={np.degrees(obj.bearing()):.1f} vel={obj.relative_speed():.1f}m/s "
                          f"conf={obj.confidence:.2f}")
                print(f"Sensors: {fused_perception.sensor_status}")
                print("------------------------\n")

    def _draw_bev(self, perception: FusedPerception, scenario_info: dict = None):
        """Draw bird's eye view of fused perception."""
        # Clear BEV image
        self.bev_img[:] = 0

        # Draw ego vehicle at center (bottom)
        ego_x = self.bev_width // 2
        ego_y = self.bev_height - 50

        # Draw ego vehicle as triangle
        triangle = np.array([
            [ego_x, ego_y - 15],  # front
            [ego_x - 10, ego_y + 10],  # rear left
            [ego_x + 10, ego_y + 10],  # rear right
        ], np.int32)
        cv2.fillPoly(self.bev_img, [triangle], (0, 255, 0))

        # Draw heading line
        heading = perception.ego_heading
        hx = int(ego_x + 30 * np.sin(heading))
        hy = int(ego_y - 30 * np.cos(heading))
        cv2.line(self.bev_img, (ego_x, ego_y), (hx, hy), (0, 255, 0), 2)

        # Draw range circles
        for r in [10, 20, 30, 40, 50]:
            radius = int(r / self.bev_range * (self.bev_height - 50))
            cv2.circle(self.bev_img, (ego_x, ego_y), radius, (50, 50, 50), 1)

        # Draw bearing lines
        for angle_deg in [-90, -60, -30, 0, 30, 60, 90]:
            angle = np.radians(angle_deg)
            x = int(ego_x + (self.bev_height - 50) * np.sin(angle))
            y = int(ego_y - (self.bev_height - 50) * np.cos(angle))
            cv2.line(self.bev_img, (ego_x, ego_y), (x, y), (30, 30, 30), 1)

        # Draw fused objects
        for obj in perception.objects:
            # Convert object position to BEV coordinates
            # Object position is in vehicle frame (x forward, y left)
            obj_x = obj.position[0]  # forward
            obj_y = obj.position[1]  # left

            # Convert to image coordinates
            # Image: x right, y down. Vehicle: x forward, y left
            ix = int(ego_x + obj_y / self.bev_range * (self.bev_height - 50))
            iy = int(ego_y - obj_x / self.bev_range * (self.bev_height - 50))

            # Check if in view
            if 0 <= ix < self.bev_width and 0 <= iy < self.bev_height:
                # Color by object class
                color = self._get_class_color(obj.object_class)

                # Draw object as circle
                radius = max(3, int(5 * obj.confidence))
                cv2.circle(self.bev_img, (ix, iy), radius, color, -1)

                # Draw velocity vector
                if obj.relative_speed() > 0.5:
                    vx = obj.velocity[0]
                    vy = obj.velocity[1]
                    vx_img = vy  # left -> right
                    vy_img = -vx  # forward -> up
                    vx_img = int(vx_img / self.bev_range * (self.bev_height - 50) * 5)
                    vy_img = int(vy_img / self.bev_range * (self.bev_height - 50) * 5)
                    cv2.arrowedLine(self.bev_img, (ix, iy),
                                   (ix + vx_img, iy + vy_img), color, 2)

                # Draw track ID
                if obj.track_id >= 0:
                    cv2.putText(self.bev_img, f"#{obj.track_id}",
                               (ix + 5, iy - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

        # Draw scenario info
        if scenario_info:
            maneuver = scenario_info.get("maneuver", "unknown")
            road_type = scenario_info.get("road_type", "unknown")
            traffic_light = scenario_info.get("traffic_light_state", "unknown")

            info_text = [
                f"Road: {road_type}",
                f"Maneuver: {maneuver}",
                f"Traffic Light: {traffic_light}",
                f"Objects: {len(perception.objects)}"
            ]
            for i, line in enumerate(info_text):
                cv2.putText(self.bev_img, line, (10, 20 + i * 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Legend
        legend_y = self.bev_height - 100
        for cls in [ObjectClass.CAR, ObjectClass.TWO_WHEELER, ObjectClass.AUTO_RICKSHAW,
                    ObjectClass.BUS, ObjectClass.PEDESTRIAN, ObjectClass.STATIC_OBSTACLE]:
            color = self._get_class_color(cls)
            cv2.rectangle(self.bev_img, (10, legend_y), (25, legend_y + 15), color, -1)
            cv2.putText(self.bev_img, cls.name, (30, legend_y + 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
            legend_y += 18

    def _get_class_color(self, obj_class: ObjectClass) -> tuple:
        """Get color for object class."""
        colors = {
            ObjectClass.CAR: (0, 255, 255),       # Yellow
            ObjectClass.TWO_WHEELER: (255, 0, 255),  # Magenta
            ObjectClass.AUTO_RICKSHAW: (255, 128, 0),  # Orange
            ObjectClass.BUS: (255, 0, 0),         # Blue (BGR)
            ObjectClass.TRUCK: (128, 0, 128),     # Purple
            ObjectClass.PEDESTRIAN: (0, 255, 0),  # Green
            ObjectClass.BICYCLE: (0, 128, 255),   # Light blue
            ObjectClass.STATIC_OBSTACLE: (128, 128, 128),  # Gray
            ObjectClass.UNKNOWN: (255, 255, 255), # White
        }
        return colors.get(obj_class, (255, 255, 255))

    def close(self):
        if OPENCV_AVAILABLE:
            cv2.destroyAllWindows()