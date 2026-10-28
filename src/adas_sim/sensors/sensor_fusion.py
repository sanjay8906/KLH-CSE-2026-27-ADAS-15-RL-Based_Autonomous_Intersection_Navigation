"""
Sensor Fusion Module for ADAS Intersection Navigation

Fuses data from multiple sensors (LiDAR, Radar, Ultrasonic, Camera, GPS, IMU)
to provide a unified, robust perception of the environment.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import numpy as np
from enum import Enum

from adas_sim.sensors.lidar import LidarSensor
from adas_sim.sensors.radar import RadarSensor
from adas_sim.sensors.ultrasonic import UltrasonicSensor
from adas_sim.sensors.camera import CameraSensor
from adas_sim.sensors.gps import GPSSensor
from adas_sim.sensors.imu import IMUSensor
from adas_sim.sensors.vehicle_state import VehicleState


class ObjectClass(Enum):
    """Classification of detected objects."""
    UNKNOWN = 0
    CAR = 1
    TWO_WHEELER = 2
    AUTO_RICKSHAW = 3
    BUS = 4
    TRUCK = 5
    PEDESTRIAN = 6
    BICYCLE = 7
    STATIC_OBSTACLE = 8


@dataclass
class FusedObject:
    """A fused object detection from multiple sensors."""
    # Position in vehicle frame (meters)
    position: np.ndarray  # [x, y, z] - x forward, y left, z up

    # Velocity in vehicle frame (m/s)
    velocity: np.ndarray  # [vx, vy, vz]

    # Object properties
    object_class: ObjectClass = ObjectClass.UNKNOWN
    confidence: float = 0.0  # 0.0 to 1.0

    # Sensor contributions
    lidar_points: int = 0
    radar_detected: bool = False
    ultrasonic_detected: bool = False
    camera_detected: bool = False

    # Bounding box (vehicle frame)
    bbox_min: Optional[np.ndarray] = None  # [x, y, z]
    bbox_max: Optional[np.ndarray] = None  # [x, y, z]

    # Tracking
    track_id: int = -1
    age: int = 0  # frames since first detection
    last_update: int = 0  # frame number

    def distance(self) -> float:
        """Get distance to object (2D)."""
        return float(np.linalg.norm(self.position[:2]))

    def relative_speed(self) -> float:
        """Get relative speed (2D)."""
        return float(np.linalg.norm(self.velocity[:2]))

    def bearing(self) -> float:
        """Get bearing angle (radians, 0 = forward, positive = left)."""
        return float(np.arctan2(self.position[1], self.position[0]))


@dataclass
class FusedPerception:
    """Complete fused perception output."""
    # Timestamp
    timestamp: float = 0.0
    frame_number: int = 0

    # Ego vehicle state
    ego_position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    ego_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    ego_heading: float = 0.0
    ego_speed: float = 0.0

    # Fused objects
    objects: List[FusedObject] = field(default_factory=list)

    # Free space / occupancy grid (optional)
    occupancy_grid: Optional[np.ndarray] = None
    grid_resolution: float = 0.5  # meters per cell
    grid_origin: np.ndarray = field(default_factory=lambda: np.zeros(2))

    # Intersection state
    intersection_info: Dict = field(default_factory=dict)
    traffic_light_state: str = "unknown"
    distance_to_intersection: float = 0.0

    # Sensor health
    sensor_status: Dict[str, bool] = field(default_factory=dict)

    def get_objects_in_front(self, max_distance: float = 50.0, fov_deg: float = 120.0) -> List[FusedObject]:
        """Get objects in front of vehicle within FOV."""
        half_fov = np.radians(fov_deg / 2.0)
        result = []
        for obj in self.objects:
            if obj.distance() <= max_distance:
                bearing = abs(obj.bearing())
                if bearing <= half_fov:
                    result.append(obj)
        return result

    def get_closest_object(self, max_distance: float = 50.0) -> Optional[FusedObject]:
        """Get closest object in front."""
        front_objects = self.get_objects_in_front(max_distance)
        if not front_objects:
            return None
        return min(front_objects, key=lambda o: o.distance())


class SensorFusion:
    """
    Fuses data from multiple sensors to create a unified perception.

    Sensors fused:
    - LiDAR: Primary 3D point cloud for obstacle detection
    - Radar: Velocity measurement for moving objects
    - Ultrasonic: Close-range detection (< 5m)
    - Camera: Object classification (placeholder for future)
    - GPS: Global position
    - IMU: Ego motion estimation
    - Vehicle State: Speed, heading, position
    """

    def __init__(
        self,
        lidar: LidarSensor,
        radar: RadarSensor,
        ultrasonic: UltrasonicSensor,
        camera: CameraSensor,
        gps: GPSSensor,
        imu: IMUSensor,
        vehicle_state: VehicleState,
        max_range: float = 50.0,
        fusion_fov_deg: float = 180.0
    ):
        self.lidar = lidar
        self.radar = radar
        self.ultrasonic = ultrasonic
        self.camera = camera
        self.gps = gps
        self.imu = imu
        self.vehicle_state = vehicle_state

        self.max_range = max_range
        self.fusion_fov_deg = fusion_fov_deg
        self.half_fov_rad = np.radians(fusion_fov_deg / 2.0)

        # Tracking
        self.next_track_id = 0
        self.tracks: Dict[int, FusedObject] = {}
        self.max_track_age = 30  # frames
        self.association_distance_threshold = 4.0  # meters (increased for better tracking)

        # Coordinate transforms
        # LiDAR is typically mounted at front center, slightly above ground
        self.lidar_to_vehicle = np.array([1.5, 0.0, 1.5])  # [x, y, z] offset
        self.radar_to_vehicle = np.array([2.0, 0.0, 0.5])
        self.ultrasonic_to_vehicle = np.array([2.5, 0.0, 0.3])

        # Traffic light state machine
        self.traffic_light_state = "green"
        self.traffic_light_timer = 0.0
        self.traffic_light_cycle = 30.0  # seconds
        self.traffic_light_green = 15.0
        self.traffic_light_yellow = 3.0
        self.traffic_light_red = 12.0

        # Frame counter
        self.frame_number = 0

        print(f"Sensor Fusion Initialized:")
        print(f"  Max Range: {max_range}m")
        print(f"  FOV: {fusion_fov_deg}°")
        print(f"  LiDAR offset: {self.lidar_to_vehicle}")
        print(f"  Radar offset: {self.radar_to_vehicle}")
        print(f"  Ultrasonic offset: {self.ultrasonic_to_vehicle}")

    def _update_traffic_light(self, dt: float = 0.1):
        """Update traffic light state machine."""
        self.traffic_light_timer += dt
        cycle_pos = self.traffic_light_timer % self.traffic_light_cycle

        if cycle_pos < self.traffic_light_green:
            self.traffic_light_state = "green"
        elif cycle_pos < self.traffic_light_green + self.traffic_light_yellow:
            self.traffic_light_state = "yellow"
        else:
            self.traffic_light_state = "red"

    def _init_traffic_light_from_config(self, scenario_config):
        """Initialize traffic light state from scenario config on first frame."""
        if self.frame_number == 1 and scenario_config is not None:
            # Check if scenario config has traffic lights
            if hasattr(scenario_config, 'traffic_lights') and scenario_config.traffic_lights:
                tl = scenario_config.traffic_lights[0]
                initial_state = getattr(tl, 'initial_state', 'green')
                if initial_state == "red":
                    # Set timer to be in red phase
                    self.traffic_light_timer = self.traffic_light_green + self.traffic_light_yellow
                    self.traffic_light_state = "red"
                elif initial_state == "yellow":
                    self.traffic_light_timer = self.traffic_light_green
                    self.traffic_light_state = "yellow"
                # For green, timer stays at 0

                # Update cycle durations from config if available
                if hasattr(tl, 'cycle_duration'):
                    self.traffic_light_cycle = tl.cycle_duration
                if hasattr(tl, 'green_duration'):
                    self.traffic_light_green = tl.green_duration
                if hasattr(tl, 'yellow_duration'):
                    self.traffic_light_yellow = tl.yellow_duration
                if hasattr(tl, 'red_duration'):
                    self.traffic_light_red = tl.red_duration

    def _compute_distance_to_intersection(self, ego_position: np.ndarray, scenario_config) -> float:
        """Compute distance from ego vehicle to intersection center."""
        # Intersection centers for different maps
        # X map: center at (50, 7)
        # T map: center at (50, 7)
        # Y map: center at (50, 7)
        intersection_center = np.array([50.0, 7.0, 0.0])
        return float(np.linalg.norm(ego_position[:2] - intersection_center[:2]))

    def process(
        self,
        raw_observation: np.ndarray,
        vehicle,
        scenario_config: Optional[object] = None
    ) -> FusedPerception:
        """
        Process all sensor data and return fused perception.

        Args:
            raw_observation: Raw observation from MetaDrive (includes LiDAR)
            vehicle: MetaDrive vehicle object
            scenario_config: Optional scenario configuration for intersection info

        Returns:
            FusedPerception with all fused objects and ego state
        """
        self.frame_number += 1
        dt = 0.1  # assuming 10Hz

        # Initialize traffic light from scenario config on first frame
        self._init_traffic_light_from_config(scenario_config)

        # Update traffic light state machine
        self._update_traffic_light(dt)

        # ----------------------------------------------------
        # 1. Process individual sensors
        # ----------------------------------------------------

        # LiDAR - primary sensor
        lidar_data = self.lidar.process(raw_observation)

        # Vehicle state - ego information
        ego_state = self.vehicle_state.process(vehicle)

        # Radar - velocity detection (pass ego speed for motion compensation)
        radar_data = self.radar.process(lidar_data, ego_speed=ego_state["speed"], ego_heading=ego_state["heading"])

        # Ultrasonic - close range
        ultrasonic_data = self.ultrasonic.process(lidar_data)

        # Camera - placeholder for future classification
        camera_image = None  # Would come from simulator

        # GPS - global position
        gps_data = self.gps.process(vehicle)

        # IMU - ego motion
        imu_data = self.imu.process(vehicle)

        # ----------------------------------------------------
        # 2. Build ego state
        # ----------------------------------------------------

        ego_position = np.array(ego_state["position"], dtype=np.float32)
        ego_speed = ego_state["speed"]
        ego_heading = ego_state["heading"]

        # Velocity vector in world frame
        ego_velocity = np.array([
            ego_speed * np.cos(ego_heading),
            ego_speed * np.sin(ego_heading),
            0.0
        ], dtype=np.float32)

        # Compute distance to intersection
        distance_to_intersection = self._compute_distance_to_intersection(ego_position, scenario_config)

        # Get intersection info from scenario config
        intersection_info = {}
        if scenario_config is not None:
            if hasattr(scenario_config, 'maneuver'):
                intersection_info["maneuver"] = scenario_config.maneuver
            if hasattr(scenario_config, 'yield_to_cross_traffic'):
                intersection_info["yield_to_cross_traffic"] = scenario_config.yield_to_cross_traffic
            if hasattr(scenario_config, 'cross_traffic'):
                intersection_info["cross_traffic"] = scenario_config.cross_traffic
            if hasattr(scenario_config, 'pedestrian_crossing'):
                intersection_info["pedestrian_crossing"] = scenario_config.pedestrian_crossing
            if hasattr(scenario_config, 'speed_limit'):
                intersection_info["speed_limit"] = scenario_config.speed_limit
            if hasattr(scenario_config, 'stop_distance'):
                intersection_info["stop_distance"] = scenario_config.stop_distance

        # ----------------------------------------------------
        # 3. Fuse LiDAR point cloud into objects
        # ----------------------------------------------------

        lidar_objects = self._lidar_to_objects(lidar_data, ego_heading)

        # ----------------------------------------------------
        # 4. Associate radar detections with LiDAR objects
        # ----------------------------------------------------

        self._associate_radar(lidar_objects, radar_data)

        # ----------------------------------------------------
        # 5. Check ultrasonic for close objects
        # ----------------------------------------------------

        self._check_ultrasonic(lidar_objects, ultrasonic_data)

        # ----------------------------------------------------
        # 6. Classify objects (placeholder - would use camera)
        # ----------------------------------------------------

        self._classify_objects(lidar_objects)

        # ----------------------------------------------------
        # 7. Track objects over time
        # ----------------------------------------------------

        fused_objects = self._update_tracks(lidar_objects)

        # ----------------------------------------------------
        # 8. Build output
        # ----------------------------------------------------

        perception = FusedPerception(
            timestamp=float(self.frame_number * 0.1),  # assuming 10Hz
            frame_number=self.frame_number,
            ego_position=ego_position,
            ego_velocity=ego_velocity,
            ego_heading=ego_heading,
            ego_speed=ego_speed,
            objects=fused_objects,
            intersection_info=intersection_info,
            traffic_light_state=self.traffic_light_state,
            distance_to_intersection=distance_to_intersection,
            sensor_status={
                "lidar": True,
                "radar": len(radar_data) > 0,
                "ultrasonic": ultrasonic_data["distance"] < self.ultrasonic.max_range,
                "camera": camera_image is not None,
                "gps": True,
                "imu": True
            }
        )

        return perception

    def _lidar_to_objects(
        self,
        lidar_data: np.ndarray,
        ego_heading: float
    ) -> List[FusedObject]:
        """Convert LiDAR point cloud to object detections."""
        objects = []
        num_lasers = len(lidar_data)

        # LiDAR covers 360 degrees, index 0 = front (0 rad)
        angle_per_laser = 2.0 * np.pi / num_lasers

        # Cluster nearby points into objects
        # Simple clustering: group consecutive points within distance threshold
        cluster_threshold = 3.5  # meters (increased further for better grouping of large vehicles)
        min_points_per_cluster = 3

        clusters = []
        current_cluster = []

        for i in range(num_lasers):
            dist = lidar_data[i]

            # Check if point is valid and within range and FOV
            angle = i * angle_per_laser
            # Normalize to [-pi, pi]
            if angle > np.pi:
                angle -= 2.0 * np.pi

            in_fov = abs(angle) <= self.half_fov_rad
            # Increased minimum range to avoid self-detection (LiDAR is mounted ~1.5m forward)
            # Vehicle front is ~2.5-3m ahead of LiDAR, so filter anything closer than 2.5m
            in_range = 2.5 < dist < self.max_range

            if in_fov and in_range:
                # Convert to vehicle frame
                x = dist * np.cos(angle) + self.lidar_to_vehicle[0]
                y = dist * np.sin(angle) + self.lidar_to_vehicle[1]
                point = np.array([x, y, self.lidar_to_vehicle[2]])
                current_cluster.append((i, point, dist, angle))
            else:
                if len(current_cluster) >= min_points_per_cluster:
                    clusters.append(current_cluster)
                current_cluster = []

        # Check last cluster
        if len(current_cluster) >= min_points_per_cluster:
            clusters.append(current_cluster)

        # Create objects from clusters
        for cluster in clusters:
            points = np.array([p[1] for p in cluster])
            distances = np.array([p[2] for p in cluster])
            angles = np.array([p[3] for p in cluster])

            # Object center (mean of points)
            center = np.mean(points, axis=0)

            # Bounding box
            bbox_min = np.min(points, axis=0)
            bbox_max = np.max(points, axis=0)

            # Calculate object size
            size = bbox_max - bbox_min
            length = size[0]
            width = size[1]

            # Estimate velocity (zero for now, radar will update)
            velocity = np.zeros(3)

            # Filter out intersection structure false positives:
            # - STATIC_OBSTACLE at intersection (traffic lights, signs, curbs)
            # These are typically at specific distances and angles from intersection center
            # We filter objects that look like infrastructure (very low height, thin, at intersection)

            # Skip objects that are likely intersection infrastructure:
            # - Very thin objects (width < 0.5m) at medium distance (15-35m)
            #   with low point count - likely poles/signs
            # - Objects that span large angular range but are far - likely curbs/walls
            # - Very small objects with few points - likely noise or small poles
            # - Objects at typical intersection infrastructure positions
            angular_span = np.max(angles) - np.min(angles)

            is_likely_infrastructure = False
            if width < 0.5 and length < 0.5 and len(cluster) < 8 and 15 < center[0] < 35:
                # Thin pole-like object at intersection distance - likely traffic light/sign
                is_likely_infrastructure = True
            elif angular_span > np.radians(30) and center[0] > 20 and len(cluster) > 30:
                # Large angular span at distance - likely curb/wall/road edge
                is_likely_infrastructure = True
            elif length < 0.8 and width < 0.8 and len(cluster) < 5:
                # Very small object with few points - likely noise or small pole
                is_likely_infrastructure = True
            elif center[0] > 40 and angular_span > np.radians(60):
                # Very large angular span far ahead - likely road boundary/curb
                is_likely_infrastructure = True
            elif width < 1.0 and length < 1.0 and len(cluster) < 10 and 20 < center[0] < 45:
                # Small compact object at intersection - likely traffic infrastructure
                is_likely_infrastructure = True

            if is_likely_infrastructure:
                # Still create object but mark as STATIC_OBSTACLE with low confidence
                obj = FusedObject(
                    position=center,
                    velocity=velocity,
                    lidar_points=len(cluster),
                    bbox_min=bbox_min,
                    bbox_max=bbox_max,
                    confidence=0.3,  # Low confidence for infrastructure
                    object_class=ObjectClass.STATIC_OBSTACLE
                )
                objects.append(obj)
            else:
                obj = FusedObject(
                    position=center,
                    velocity=velocity,
                    lidar_points=len(cluster),
                    bbox_min=bbox_min,
                    bbox_max=bbox_max,
                    confidence=min(1.0, len(cluster) / 20.0)
                )
                objects.append(obj)

        # Merge nearby objects that are likely the same (over-clustering fix)
        objects = self._merge_nearby_objects(objects)

        # Post-merge: Filter out low-confidence STATIC_OBSTACLE objects that are likely infrastructure
        # These are typically at intersection distances with low point counts
        filtered_objects = []
        for obj in objects:
            if obj.object_class == ObjectClass.STATIC_OBSTACLE and obj.confidence < 0.5:
                # Check if it's at typical infrastructure positions
                dist = obj.distance()
                bearing = abs(obj.bearing())
                # Filter: static obstacles at intersection (15-45m ahead, wide angle) with low confidence
                if 15 < dist < 45 and bearing > np.radians(20) and obj.lidar_points < 15:
                    # Likely intersection infrastructure (curb, traffic light pole, sign)
                    continue
                # Filter: very close static obstacles with few points (noise)
                if dist < 5.0 and obj.lidar_points < 8:
                    continue
            filtered_objects.append(obj)

        return filtered_objects

    def _merge_nearby_objects(self, objects: List[FusedObject], merge_threshold: float = 3.5) -> List[FusedObject]:
        """Merge objects that are close together and likely the same object."""
        if not objects:
            return objects

        merged = []
        used = set()

        for i, obj1 in enumerate(objects):
            if i in used:
                continue

            # Find nearby objects to merge
            merge_group = [obj1]
            used.add(i)

            for j, obj2 in enumerate(objects):
                if j in used or i == j:
                    continue

                dist = np.linalg.norm(obj1.position[:2] - obj2.position[:2])
                # Also consider velocity similarity for moving objects
                vel_similar = np.linalg.norm(obj1.velocity[:2] - obj2.velocity[:2]) < 2.0

                # Use larger threshold for static/large objects (trucks, buses, static obstacles)
                # These tend to create multiple clusters from different parts of the same object
                # Determine if "large" based on bbox size or point count (since class is UNKNOWN at this stage)
                obj1_static = obj1.relative_speed() < 1.0
                obj2_static = obj2.relative_speed() < 1.0

                # Heuristic: large vehicles have large bbox or many lidar points
                obj1_large = False
                obj2_large = False
                if obj1.bbox_min is not None and obj1.bbox_max is not None:
                    size1 = obj1.bbox_max - obj1.bbox_min
                    obj1_large = size1[0] > 6.0 or size1[1] > 2.5 or obj1.lidar_points > 25
                if obj2.bbox_min is not None and obj2.bbox_max is not None:
                    size2 = obj2.bbox_max - obj2.bbox_min
                    obj2_large = size2[0] > 6.0 or size2[1] > 2.5 or obj2.lidar_points > 25

                effective_threshold = merge_threshold
                if (obj1_static and obj2_static) or (obj1_large and obj2_large):
                    # More aggressive merging for static objects and large vehicles
                    effective_threshold = max(merge_threshold, 8.0)

                # Also merge if objects are at very similar bearing (same object, different parts)
                bearing_diff = abs(obj1.bearing() - obj2.bearing())
                if bearing_diff < np.radians(10) and dist < 10.0:
                    # Very similar bearing and close - likely same large object
                    effective_threshold = max(effective_threshold, 10.0)

                if dist < effective_threshold:
                    # For static objects, be more aggressive in merging
                    # For moving objects, also check velocity similarity
                    if obj1_static and obj2_static:
                        # Both static - merge if close
                        merge_group.append(obj2)
                        used.add(j)
                    elif vel_similar:
                        # Both moving with similar velocity - merge if close
                        merge_group.append(obj2)
                        used.add(j)

            # Merge the group
            if len(merge_group) == 1:
                merged.append(obj1)
            else:
                # Weighted average by confidence/point count
                total_points = sum(o.lidar_points for o in merge_group)
                if total_points == 0:
                    total_points = 1

                merged_pos = np.zeros(3)
                merged_vel = np.zeros(3)
                max_confidence = 0
                merged_bbox_min = None
                merged_bbox_max = None
                merged_class = ObjectClass.UNKNOWN

                for o in merge_group:
                    weight = o.lidar_points / total_points
                    merged_pos += o.position * weight
                    merged_vel += o.velocity * weight
                    max_confidence = max(max_confidence, o.confidence)

                    if o.bbox_min is not None and o.bbox_max is not None:
                        if merged_bbox_min is None:
                            merged_bbox_min = o.bbox_min.copy()
                            merged_bbox_max = o.bbox_max.copy()
                        else:
                            merged_bbox_min = np.minimum(merged_bbox_min, o.bbox_min)
                            merged_bbox_max = np.maximum(merged_bbox_max, o.bbox_max)

                # Use highest confidence class
                for o in merge_group:
                    if o.confidence == max_confidence:
                        merged_class = o.object_class
                        break

                merged_obj = FusedObject(
                    position=merged_pos,
                    velocity=merged_vel,
                    object_class=merged_class,
                    confidence=min(1.0, max_confidence + 0.1),
                    lidar_points=total_points,
                    radar_detected=any(o.radar_detected for o in merge_group),
                    ultrasonic_detected=any(o.ultrasonic_detected for o in merge_group),
                    camera_detected=any(o.camera_detected for o in merge_group),
                    bbox_min=merged_bbox_min,
                    bbox_max=merged_bbox_max,
                    track_id=-1,
                    age=1,
                    last_update=self.frame_number
                )
                merged.append(merged_obj)

        return merged

    def _associate_radar(
        self,
        lidar_objects: List[FusedObject],
        radar_data: List[Dict]
    ):
        """Associate radar detections with LiDAR objects."""
        if not radar_data:
            return

        for radar_det in radar_data:
            radar_dist = radar_det["distance"]
            radar_vel = radar_det["velocity"]  # Object radial velocity in vehicle frame (m/s)
            radar_idx = radar_det["index"]

            # Find closest LiDAR object
            best_obj = None
            best_dist = float('inf')

            for obj in lidar_objects:
                dist = abs(obj.distance() - radar_dist)
                if dist < best_dist and dist < self.association_distance_threshold:
                    best_dist = dist
                    best_obj = obj

            if best_obj is not None:
                best_obj.radar_detected = True

                # Radar measures radial velocity in vehicle frame: vr = vx*cos(θ) + vy*sin(θ)
                # We can't uniquely determine vx, vy from just vr and θ.
                # For objects roughly ahead (|bearing| < 30°), estimate longitudinal velocity
                bearing = best_obj.bearing()
                cos_bearing = np.cos(bearing)

                # Sanity check: radar velocity should be reasonable
                # Clamp to max reasonable speed (50 m/s = 180 km/h)
                max_speed = 50.0
                if abs(radar_vel) > max_speed:
                    # Radar velocity is unreasonable - skip radar update for this object
                    best_obj.confidence = min(1.0, best_obj.confidence + 0.1)
                    continue

                if abs(bearing) < np.radians(30) and abs(cos_bearing) > 0.1:
                    # Object roughly ahead - estimate longitudinal velocity
                    # vr ≈ vx * cos(θ) => vx ≈ vr / cos(θ)
                    vx_est = radar_vel / cos_bearing
                    # Sanity check on estimated longitudinal velocity
                    if abs(vx_est) <= max_speed:
                        best_obj.velocity[0] = vx_est
                    else:
                        # Fallback: use radial velocity directly
                        best_obj.velocity[0] = radar_vel * cos_bearing
                else:
                    # Object to the side - radial velocity doesn't give good longitudinal estimate
                    # Use a conservative estimate: assume object moves along bearing direction
                    best_obj.velocity[0] = radar_vel * cos_bearing
                    best_obj.velocity[1] = radar_vel * np.sin(bearing)

                best_obj.confidence = min(1.0, best_obj.confidence + 0.2)

    def _check_ultrasonic(
        self,
        lidar_objects: List[FusedObject],
        ultrasonic_data: Dict
    ):
        """Check ultrasonic sensor for close-range confirmation."""
        ultra_dist = ultrasonic_data["distance"]
        ultra_max = ultrasonic_data["max_range"]

        if ultra_dist < ultra_max:
            # Check if any LiDAR object matches ultrasonic distance
            for obj in lidar_objects:
                if abs(obj.distance() - ultra_dist) < 1.0:
                    obj.ultrasonic_detected = True
                    obj.confidence = min(1.0, obj.confidence + 0.15)
                    break
            else:
                # No matching LiDAR object - create a close-range object
                # Ultrasonic is forward-facing, so place object directly ahead
                obj = FusedObject(
                    position=np.array([ultra_dist, 0.0, 0.3]),
                    velocity=np.zeros(3),
                    ultrasonic_detected=True,
                    confidence=0.7
                )
                lidar_objects.append(obj)

    def _classify_objects(self, objects: List[FusedObject]):
        """Classify objects based on size, velocity, and context (placeholder)."""
        for obj in objects:
            # Simple classification based on size and velocity
            if obj.bbox_min is not None and obj.bbox_max is not None:
                size = obj.bbox_max - obj.bbox_min
                length = size[0]
                width = size[1]

                speed = obj.relative_speed()

                # Heuristic classification
                if length < 1.5 and width < 1.0 and speed < 2.0:
                    obj.object_class = ObjectClass.PEDESTRIAN
                elif length < 2.5 and width < 1.2:
                    if speed > 5.0:
                        obj.object_class = ObjectClass.TWO_WHEELER
                    else:
                        obj.object_class = ObjectClass.AUTO_RICKSHAW
                elif length < 5.0 and width < 2.0:
                    obj.object_class = ObjectClass.CAR
                elif length < 8.0 and width < 2.5:
                    obj.object_class = ObjectClass.BUS
                elif length >= 8.0:
                    obj.object_class = ObjectClass.TRUCK
                else:
                    obj.object_class = ObjectClass.STATIC_OBSTACLE
            else:
                # No bbox, use point count
                if obj.lidar_points < 5:
                    obj.object_class = ObjectClass.PEDESTRIAN
                elif obj.lidar_points < 15:
                    obj.object_class = ObjectClass.TWO_WHEELER
                else:
                    obj.object_class = ObjectClass.CAR

    def _update_tracks(self, detections: List[FusedObject]) -> List[FusedObject]:
        """Update object tracks with new detections."""
        # Simple tracking: associate detections with existing tracks by distance
        updated_tracks = {}
        used_detections = set()

        # Try to match each track with a detection
        for track_id, track in self.tracks.items():
            best_det_idx = None
            best_dist = float('inf')

            for i, det in enumerate(detections):
                if i in used_detections:
                    continue
                dist = np.linalg.norm(det.position[:2] - track.position[:2])
                if dist < best_dist and dist < self.association_distance_threshold * 2:
                    best_dist = dist
                    best_det_idx = i

            if best_det_idx is not None:
                best_det = detections[best_det_idx]
                # Update track with detection
                best_det.track_id = track_id
                best_det.age = track.age + 1
                best_det.last_update = self.frame_number
                # Smooth position
                alpha = 0.7
                best_det.position = alpha * best_det.position + (1 - alpha) * track.position
                best_det.velocity = alpha * best_det.velocity + (1 - alpha) * track.velocity
                used_detections.add(best_det_idx)
                updated_tracks[track_id] = best_det
            else:
                # Track not updated - keep prediction
                track.age += 1
                track.last_update = self.frame_number
                # Predict position based on velocity
                track.position[:2] += track.velocity[:2] * 0.1  # dt = 0.1s
                if track.age < self.max_track_age:
                    updated_tracks[track_id] = track

        # Create new tracks for unmatched detections
        for i, det in enumerate(detections):
            if i not in used_detections:
                det.track_id = self.next_track_id
                det.age = 1
                det.last_update = self.frame_number
                updated_tracks[self.next_track_id] = det
                self.next_track_id += 1

        self.tracks = updated_tracks
        return list(updated_tracks.values())

    def reset(self):
        """Reset fusion state."""
        self.next_track_id = 0
        self.tracks = {}
        self.frame_number = 0

        # Reset individual sensors
        if hasattr(self.radar, 'reset'):
            self.radar.reset()
        if hasattr(self.ultrasonic, 'reset'):
            self.ultrasonic.reset()
        if hasattr(self.gps, 'reset'):
            self.gps.reset()
        if hasattr(self.imu, 'reset'):
            self.imu.reset()

    def get_stats(self) -> Dict:
        """Get fusion statistics."""
        return {
            "num_tracks": len(self.tracks),
            "frame_number": self.frame_number,
            "max_range": self.max_range,
            "fov_deg": self.fusion_fov_deg
        }


def create_sensor_fusion(
    lidar: LidarSensor,
    radar: RadarSensor,
    ultrasonic: UltrasonicSensor,
    camera: CameraSensor,
    gps: GPSSensor,
    imu: IMUSensor,
    vehicle_state: VehicleState,
    max_range: float = 50.0,
    fusion_fov_deg: float = 180.0
) -> SensorFusion:
    """Factory function to create SensorFusion instance."""
    return SensorFusion(
        lidar=lidar,
        radar=radar,
        ultrasonic=ultrasonic,
        camera=camera,
        gps=gps,
        imu=imu,
        vehicle_state=vehicle_state,
        max_range=max_range,
        fusion_fov_deg=fusion_fov_deg
    )


if __name__ == "__main__":
    # Test the sensor fusion
    print("Testing Sensor Fusion...")

    # Create sensors
    lidar = LidarSensor(num_lasers=240)
    radar = RadarSensor()
    ultrasonic = UltrasonicSensor()
    camera = CameraSensor()
    gps = GPSSensor()
    imu = IMUSensor()
    vehicle_state = VehicleState()

    # Create fusion
    fusion = create_sensor_fusion(lidar, radar, ultrasonic, camera, gps, imu, vehicle_state)

    print("Sensor Fusion created successfully!")
    print(f"Stats: {fusion.get_stats()}")