# -*- coding: utf-8 -*-

import os
from pathlib import Path
from omni.isaac.kit import SimulationApp

LUMI_STAGE_PATH = "/World/jaka_lumi"
# LUMI_USD_PATH   = "/home/meddy/jaka_lumi_ros/src/jaka_lumi_description/urdf/jaka_lumi/jaka_lumi_moveit.usd"
GRAPH_PATH = "/ActionGraph"
CONFIG = {"renderer": "RayTracedLighting", "headless": False}

simulation_app = SimulationApp(CONFIG)

from isaacsim.core.api import SimulationContext
from isaacsim.core.utils import extensions
from omni.usd import get_context
from pxr import Usd

extensions.enable_extension("isaacsim.ros2.bridge")
extensions.enable_extension("isaacsim.ros2.urdf")
extensions.enable_extension("isaacsim.ros2.tf_viewer")
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

# Run app update for multiple frames to re-initialize the ROS action graph after setting new prim inputs
simulation_app.update()
simulation_app.update()

simulation_context.play()
simulation_app.update()

while simulation_app.is_running():

    # Run with a fixed step size
    simulation_context.step(render=True)

simulation_context.stop()
simulation_app.close()