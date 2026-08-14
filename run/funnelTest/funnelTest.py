# -*- encoding=utf-8 -*-

# import packages
from yade import plot, pack
import numpy as np
import sys
import os
from timeit import default_timer

# ============================================================
# SIMULATION PARAMETERS
# ============================================================

# Funnel geometry
r1, z1, r2, z2 = 5, 30, 1, 10

# Gravitational acceleration
gravity = (0.0, 0.0, -9.81)

# Results
outputDir = "results"
outputDirTmp = os.path.join(outputDir, 'tmp')
os.makedirs(outputDirTmp, exist_ok=True)


# ============================================================
# SIMULATION CONTROL
# ============================================================

prefix = os.path.join(outputDirTmp, 'p1-')

# Main simulation loop
O.engines = [
        ForceResetter(),
        InsertionSortCollider(
            [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb(), Bo1_Wall_Aabb()]
        ),
        InteractionLoop(
            [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom(), Ig2_Wall_Sphere_ScGeom()],
            [Ip2_FrictMat_FrictMat_FrictPhys()],
            [Law2_ScGeom_FrictPhys_CundallStrack()]
        ),
        NewtonIntegrator(
            gravity=gravity
        ),
        VTKRecorder(
            iterPeriod=1000, fileName=prefix, recorders=['spheres', 'facets']
        ),
        PyRunner(command="print(O.iter)", iterPeriod=1000)
]

# ============================================================
# SCENE CONSTRUCTION
# ============================================================

# Simulation boundary
thetas = np.linspace(0, 2*pi, 16, endpoint=True)
meridians = [
    [Vector3(r1*sin(th), r1*cos(th), z1) for th in thetas],
    [Vector3(r2*sin(th), r2*cos(th), z2) for th in thetas]
]

surf = pack.sweptPolylines2gtsSurface(meridians)
O.bodies.append(pack.gtsSurface2Facets(surf))

closedSurf = pack.sweptPolylines2gtsSurface(meridians, threshold=1e-4, capStart=True, capEnd=True)
pred = pack.inGtsSurface(closedSurf)

# Cloud of spherical particles
sp = pack.SpherePack()
sp.makeCloud(*pred.aabb(), rMean=0.2, rRelFuzz=0.3)
sp = pack.filterSpherePack(pred, sp, returnSpherePack=True)
spIDs = sp.toSimulation()
print(len(spIDs))

O.bodies.append(wall(position=0, axis=2))

# ============================================================
# SIMULATION
# ============================================================

# Set critical timestep
O.dt = PWaveTimeStep()
print(f'Critical timestep set to {O.dt:.5e}')

# Run simulation
O.saveTmp()
t = default_timer()
O.run(20001, True)
print(f'Simulation took {default_timer()-t} s')

# exit yade manually
sys.exit(0)