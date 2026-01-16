# -*- encoding=utf-8 -*-

# import packages
from yade import plot
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
    "gamma":0.2,
    "en":0.4
}
theMatBox = {
    "young":210e+6, 
    "poisson":0.3, 
    "frictionAngle":radians(35), 
    "density":7870, 
    "label":"Fe"
}

# Limit velocity at which to stop simulation
limitVelo = 1e-3

# Results
outputDir = "results"
try:
    os.mkdir(outputDir)
except FileExistsError:
    print("Directory already exists")


# ============================================================
# SIMULATION CONTROL
# ============================================================

# PyRunner add data to plots
def addPlotData():
    plot.addData(
        t=O.time, 
        coordNum=avgNumInteractions(), 
        unForce=unbalancedForce(), 
        Etot=O.energy.total(), 
        **O.energy
    )

# PyRunner track kinetic energy
def checkKinetic():
    # current kinetic energy
    ke = kineticEnergy()
    print(f'current kinetic energy: {ke:.4e}')

    if ke < limitKE:
        # Stop simulation
        O.pause()
        O.save(os.path.join(outputDir, "simulation.yade"))
        print(f'simulation stopped at iteration {O.iter}')

        # Save results
        sp.fromSimulation()
        sp.save(os.path.join(outputDir, "spherePack"))
        plot.saveDataTxt(os.path.join(outputDir, "tableData"))

# Main simulation loop
O.engines = [
    # Reset forces
    ForceResetter(),

    # Fast collision detection
    InsertionSortCollider(
        [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb()]
    ),

    # Interaction physics
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_MindlinPhys(gamma=theMatFunctor["gamma"], en=theMatFunctor["en"])],
        [Law2_ScGeom_MindlinPhys_Mindlin(includeAdhesion=True)],
    ),

    # Time integration
    NewtonIntegrator(gravity=gravity),

    # Logging and controls
    PyRunner(command='addPlotData()', iterPeriod=200),
    PyRunner(command='checkKinetic()', iterPeriod=10000)
]

# ============================================================
# SCENE CONSTRUCTION
# ============================================================

# Simulation boundary
theBoxCenter = tuple(0.5*x for x in theBox)
O.bodies.append(
    geom.facetBox(
        theBoxCenter, 
        theBoxCenter, 
        wallMask=31,
        material=FrictMat(**theMatBox)
    )
)

# Cloud of spherical particles
sp = pack.SpherePack()
sp.makeCloud((0,0,0), theBox, **theParticleDist)
spIDs = sp.toSimulation(material=FrictMat(**theMat))
print(f'Added {len(sp)} particles to simulation')    

# Stopping criterion based on average velocity
totalMass = sum(O.bodies[i].state.mass for i in spIDs)
limitKE = 0.5 * totalMass * limitVelo ** 2
print(f'Stop simulation if kinetic energy drops below {limitKE}')

# Initialize cloud with mean falling velocity in z-direction
meanVelo = -np.sqrt(np.abs(theBox[2] * gravity[2]) * 0.5)
for spID in spIDs:
    O.bodies[spID].state.vel[2] = meanVelo
print(f'Particles initialized with velocity {meanVelo:.5e}')

# Track energies
O.trackEnergy = True

# Define plots
plot.plots = {'t': ('coordNum', 'unForce'), 't ': (O.energy.keys, None, 'Etot')}


# ============================================================
# SIMULATION
# ============================================================

# Set critical timestep
O.dt = 0.5 * PWaveTimeStep()
print(f'Critical timestep set to {O.dt:.5e}')

# Run simulation
t = default_timer()
O.run(1000000, True)
print(f'Simulation took {default_timer()-t} s')

# Save plots to file
figs = plot.plot(subPlots=False, noShow=True)
for i, fig in enumerate(figs):
    fig.savefig(os.path.join(outputDir, f"fig{i}.pdf"))

# exit yade manually
sys.exit(0)