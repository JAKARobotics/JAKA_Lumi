# -*- coding: utf-8 -*-

import os
from pathlib import Path
from isaacsim import SimulationApp

LUMI_STAGE_PATH = "/World/jaka_lumi"
# LUMI_USD_PATH   = "/home/meddy/jaka_lumi_ros/src/jaka_lumi_description/urdf/jaka_lumi/jaka_lumi_moveit.usd"
GRAPH_PATH = "/ActionGraph"
CONFIG = {"renderer": "RayTracedLighting", "headless": False}

simulation_app = SimulationApp(CONFIG)

from isaacsim.core.api import SimulationContext
from isaacsim.core.utils import extensions
from omni.usd import get_context
from pxr import Sdf
import omni.graph.core as og

# extensions.enable_extension("isaacsim.code_editor.vscode")
# extensions.enable_extension("omni.kit.debug.vscode")

def _resolve_usd():
    p = os.environ.get("LUMI_USD_PATH", "")
    if p:
        return p
    try:
        from ament_index_python.packages import get_package_share_directory
        pkg_share = get_package_share_directory("jaka_lumi_description")
        return str(Path(pkg_share) / "urdf/jaka_lumi/jaka_lumi_moveit.usd")
    except Exception:
        return str(Path(__file__).resolve().parents[2] /
                   "jaka_lumi_description/urdf/jaka_lumi/jaka_lumi_moveit.usd")

LUMI_USD_PATH = _resolve_usd()

print(f"🚀 Isaac Sim starting, loading USD: {LUMI_USD_PATH}")

lumi_stage = get_context().open_stage(f"file://{LUMI_USD_PATH}")
# if not isinstance(lumi_stage, Usd.Stage):
#     raise RuntimeError("Failed to open stage.")

print("Stage Opened")

lumi_prim = get_context().get_stage().GetPrimAtPath(LUMI_STAGE_PATH)
print("Prim found:", bool(lumi_prim) and lumi_prim.IsValid())

if not lumi_prim or not lumi_prim.IsValid():
    raise RuntimeError(f"Prim not found: {LUMI_STAGE_PATH}")

# list children (quick view of links)
print("Children names under /jaka_lumi:")
for c in lumi_prim.GetChildren():
    print("  -", c.GetName(), c.GetTypeName())


simulation_context = SimulationContext(stage_units_in_meters=1.0)

# Initialize the stage first, then enable the ROS extensions before starting the simulation.
extensions.enable_extension("isaacsim.ros2.bridge")
extensions.enable_extension("isaacsim.ros2.urdf")
extensions.enable_extension("isaacsim.ros2.tf_viewer")

# The saved graph is loaded before the ROS bridge extension, so its ROS nodes are not registered as OmniGraph nodes. 
# Recreate it now that the bridge is active.
stage = get_context().get_stage()
stage.RemovePrim(GRAPH_PATH)
keys = og.Controller.Keys
og.Controller.edit(
    {"graph_path": GRAPH_PATH, "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
            ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ("Context", "isaacsim.ros2.bridge.ROS2Context"),
            ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
            ("SubscribeJointState", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
            ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
        ],
        keys.CONNECT: [
            ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "SubscribeJointState.inputs:execIn"),
            ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
            ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
            ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
            ("Context.outputs:context", "PublishClock.inputs:context"),
            ("Context.outputs:context", "PublishJointState.inputs:context"),
            ("Context.outputs:context", "SubscribeJointState.inputs:context"),
            ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
            ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
            ("SubscribeJointState.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
            ("SubscribeJointState.outputs:effortCommand", "ArticulationController.inputs:effortCommand"),
        ],
        keys.SET_VALUES: [
            ("Context.inputs:useDomainIDEnvVar", True),
            ("PublishClock.inputs:topicName", "/jaka_lumi/clock"),
            ("PublishJointState.inputs:targetPrim", [Sdf.Path(f"{LUMI_STAGE_PATH}/world")]),
            ("PublishJointState.inputs:topicName", "isaac_joint_states"),
            ("SubscribeJointState.inputs:topicName", "isaac_joint_commands"),
            ("ArticulationController.inputs:robotPath", LUMI_STAGE_PATH),
        ],
    },
)
print("ROS joint command/state graph ready")

simulation_app.update()
simulation_app.update()

simulation_context.play()
simulation_app.update()

while simulation_app.is_running():

    # Run with a fixed step size
    simulation_context.step(render=True)

simulation_context.stop()
simulation_app.close()
