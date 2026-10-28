# Implementation Plan: Intersection Scenarios & Sensor Fusion

## Current State Analysis
- ✅ Basic project structure with MetaDrive integration
- ✅ 11 intersection scenarios defined as data classes
- ✅ 7 sensors implemented (LiDAR, Camera, Radar, Ultrasonic, GPS, IMU, VehicleState)
- ✅ Basic manual/auto vehicle controller
- ✅ Sensor display with OpenCV visualization
- ❌ Scenarios don't actually configure different vehicle positions/targets
- ❌ No sensor fusion - sensors processed independently
- ❌ Auto driving is simple lane follower, not intersection-aware
- ❌ Traffic is generic, not scenario-specific mixed-density

## Phase 1: Enhanced Intersection Scenarios
### 1.1 Scenario Configuration System
- Create `ScenarioConfigurator` that maps each scenario to:
  - Vehicle spawn position (different incoming lanes)
  - Target destination (different outgoing lanes)
  - Traffic light state and timing
  - Cross-traffic configuration
  - Pedestrian crossing zones

### 1.2 MetaDrive Map Customization
- Configure vehicle initial position per scenario
- Set navigation target per scenario
- Configure traffic density and vehicle types for mixed traffic
- Add traffic light objects at intersections

### 1.3 Mixed-Density Traffic for Indian Roads
- Car traffic (4-wheelers)
- Two-wheeler traffic (motorcycles, scooters)
- Pedestrian traffic
- Auto-rickshaw / three-wheeler traffic
- Bus / public transport traffic

## Phase 2: Sensor Fusion
### 2.1 SensorFusion Class
- Fuse LiDAR + Radar + Ultrasonic for obstacle detection
- Coordinate transformation (sensor frames → vehicle frame → world frame)
- Kalman filter for tracking dynamic obstacles
- Fused obstacle list with position, velocity, classification

### 2.2 Unified Observation Builder
- Combine fused sensor data + vehicle state + intersection info
- Output structured observation for RL agent
- Handle missing/noisy sensor data gracefully

## Phase 3: Intersection-Aware Vehicle Controller
### 3.1 Scenario-Aware Auto Driving
- Detect intersection approach
- Respect traffic lights (red/yellow/green)
- Handle yield scenarios
- Execute turns (left, right, U-turn) at intersections
- Navigate T-junctions and Y-junctions

### 3.2 Behavior Planning
- High-level maneuver planning (go straight, turn left, turn right, yield, stop)
- Speed planning for intersection crossing
- Gap acceptance for unprotected turns

## Phase 4: Enhanced Manual Testing
### 4.1 Scenario Selector UI
- Keyboard shortcuts to switch scenarios
- Visual indicators for current scenario
- Traffic density adjustment

### 4.2 Improved Sensor Display
- Fused obstacle visualization
- Intersection state overlay
- Traffic light status
- Vehicle trajectory preview

## Implementation Order
1. Create `scenario_configurator.py` - maps scenarios to MetaDrive configs
2. Update `MetaDriveSimulator` to use scenario configurator
3. Create `sensor_fusion.py` - fuse all sensor data
4. Update `main.py` to use sensor fusion
5. Enhance `vehicle_controller.py` with intersection awareness
6. Add mixed-density traffic configuration
7. Test manually with all scenarios