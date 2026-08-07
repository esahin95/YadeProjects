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

# Box dimensions
theBox = (200e-6, 800e-6, 200e-6)

# Gravitational acceleration
gravity = (0.0, 0.0, -9.81)

# Particle distribution
theParticleDist = {"psdSizes":[15e-6, 45e-6], "psdCumm":[0.0, 1.0]}

# Material parameters (scaled young modulus with 1e-3)
theMat = {
    "young":130e+6,
    "poisson":0.34,
    "frictionAngle":radians(30),
    "density":8960,
    "label":"Cu"
}
theMatFunctor = {
    "gamma":0.01,
    "en":0.4
}
theMatBox = {
    "young":210e+6,
    "poisson":0.3,
    "frictionAngle":radians(35),
    "density":7870,
    "label":"Fe"
}

# Results
outputDir = "results"
os.makedirs(outputDir, exist_ok=True)


# ============================================================
# SIMULATION CONTROL
# ============================================================

# Main simulation loop
O.engines = [
        ForceResetter(),
        InsertionSortCollider(
            [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb()]
        ),
        InteractionLoop(
            [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom()],
            [Ip2_FrictMat_FrictMat_FrictPhys()],
            [Law2_ScGeom_FrictPhys_CundallStrack()]
        ),
        NewtonIntegrator(
            gravity=gravity
        )
]

# ============================================================
# SCENE CONSTRUCTION
# ============================================================

t = default_timer()

# Simulation boundary
thetas = np.linspace(0, 2*pi, 16, endpoint=True)
meridians = pack.revolutionSurfaceMeridians(
        [[(3 + rad * sin(th), 10 * rad + rad * cos(th)) for th in thetas] for rad in np.linspace(1, 2, num=10)], np.linspace(0, pi, num=10)
)
meridians += [[Vector3(5 * sin(-th), -10 + 5 * cos(-th), 30) for th in thetas]]

surf = pack.sweptPolylines2gtsSurface(meridians)
O.bodies.append(pack.gtsSurface2Facets(surf))

closedSurf = pack.sweptPolylines2gtsSurface(meridians[-2:], threshold=1e-4, capStart=True, capEnd=True)
pred = pack.inGtsSurface(closedSurf)

# Cloud of spherical particles
sp = pack.SpherePack()
sp.makeCloud(*pred.aabb(), rMean=0.2, rRelFuzz=0.3)
sp = pack.filterSpherePack(pred, sp, returnSpherePack=True)
spIDs = sp.toSimulation()
print(len(spIDs))

print(f'Scene construction took {default_timer()-t} s')

# ============================================================
# SIMULATION
# ============================================================

# Set critical timestep
O.dt = PWaveTimeStep()
print(f'Critical timestep set to {O.dt:.5e}')

t = default_timer()

# Run simulation
O.saveTmp()
O.run(8500)

print(f'Simulation took {default_timer()-t} s')

# exit yade manually
#sys.exit(0)