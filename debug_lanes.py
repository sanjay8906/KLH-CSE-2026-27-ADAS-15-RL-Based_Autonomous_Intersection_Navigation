from metadrive import MetaDriveEnv
import numpy as np

env = MetaDriveEnv({'map': 'X', 'use_render': False, 'traffic_density': 0.1})
obs, info = env.reset()

print("Vehicle position:", env.agent.position)
print("Vehicle heading:", env.agent.heading_theta)
print("Vehicle lane:", env.agent.lane)
print("Vehicle lane index:", env.agent.lane_index)

# Check road network
road_network = env.engine.current_map.road_network
print("\nRoad network graph:")
for node, edges in road_network.graph.items():
    print(f"  {node} -> {list(edges.keys())}")

# Get all lanes from the graph edges
print("\nAll lanes from graph:")
for node, edges in road_network.graph.items():
    for edge_id, lane_list in edges.items():
        if isinstance(lane_list, list):
            for i, lane in enumerate(lane_list):
                print(f"  {edge_id}[{i}]: start={lane.start}, end={lane.end}, length={lane.length:.1f}")
        else:
            print(f"  {edge_id}: start={lane_list.start}, end={lane_list.end}, length={lane_list.length:.1f}")

# Check the default spawn position (5, 7) - what lane is it on?
# The default lane index is ('>', '>>', 0)
# Let's check what lane that is
print("\n--- Default spawn lane info ---")
lane_idx = ('>', '>>', 0)
print(f"Lane index: {lane_idx}")

env.close()