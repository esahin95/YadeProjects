# -*- encoding=utf-8 -*-

# packages
import numpy as np
import sys
import os

# ============================================================
# PARAMETERS
# ============================================================

# Powder layer thickness
lth = 40e-6

# Results directory
outputDir = "results"

# ============================================================
# EXTRACT POWDERBED
# ============================================================

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load(os.path.join(outputDir, "spherePack"))
IDs = spherePack.toSimulation()

# extract spheres inside layer
for i, (center, radius) in enumerate(spherePack):
    if center[2] + radius > lth:
        O.bodies.erase(IDs[i])
spherePack.fromSimulation()
spherePack.save(os.path.join(outputDir, "powderBed"))

# exit yade manually
sys.exit(0)