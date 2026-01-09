# -*- encoding=utf-8 -*-

# packages
import numpy as np
import sys

# powder layer thickness
lth = 40e-6

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load('results/spherePack.txt')
IDs = spherePack.toSimulation()

# extract spheres inside layer
for i, (center, radius) in enumerate(spherePack):
    if center[2] + radius > lth:
        O.bodies.erase(IDs[i])
spherePack.fromSimulation()
spherePack.save('results/powderBed')

# exit yade manually
#sys.exit(0)