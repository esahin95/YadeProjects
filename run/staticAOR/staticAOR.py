# -*- encoding=utf-8 -*-

# import packages
from yade import plot, pack
import numpy as np
from scipy.stats import lognorm
import sys
import os
from timeit import default_timer

# ============================================================
# SIMULATION PARAMETERS
# ============================================================

# Funnel geometry
dOutput = 0.4e-3
dBunker = 2e-3
hBunker = 2e-3 # 2e-3
hOutput = 0.4e-3
hPipe = 0.2e-3
zHeight = 1.5e-3

# Gravitational acceleration
gravity = (0.0, 0.0, -9.81)

# Material parameters
theMat = {
    "young":130e+5,
    "poisson":0.34,
    "frictionAngle":radians(30),
    "density":89600,
    "label":"Cu"
}
theMatFunctor = {
    "gamma":1e-4,
    "en":0.4
}
theMatArt = {
    "young":theMat["young"],
    "poisson":theMat["poisson"],
    "frictionAngle":radians(0),
    "density":theMat["density"],
    "label":"Art"
}

# Powder parameters
d10 = 70e-6 # 15e-6
d90 = 80e-6 # 45e-6

# Limit velocity at which to stop simulation
limitVelo = 2e-3

# Results
outputDir = "results"
outputTmp = os.path.join(outputDir, "tmp")
os.makedirs(outputTmp, exist_ok=True)


# ============================================================
# PARTICLE SIZE DISTRIBUTION
# ============================================================

mu  = 0.5*(np.log(d90) + np.log(d10))
std = 0.5*(np.log(d90) - np.log(d10)) / 1.2816
rv = lognorm(s=std, scale=np.exp(mu))

D = rv.rvs(1000000)
D = D[np.logical_and(D>d10, D<d90)]
counts2, psdSizes = np.histogram(D, bins=30, range=(d10, d90), density=True)
psdCumm = np.hstack((0, np.cumsum(counts2*(psdSizes[1:]-psdSizes[:-1]))))
theParticleDist = {"psdSizes":psdSizes, "psdCumm":psdCumm}


# ============================================================
# SCENE CONSTRUCTION
# ============================================================

# Materials
matOfSphere = O.materials.append(FrictMat(**theMat))
matOfFunnel = O.materials.append(FrictMat(**theMatArt))

# Funnel
r1 = 0.5*dOutput
r2 = 0.5*dBunker
z1 = zHeight + hPipe
z2 = z1 + hOutput
z3 = z2 + hBunker
thetas = np.linspace(0, 2*pi, 16, endpoint=True)
meridians = [
    [Vector3(r2*sin(th), r2*cos(th), z3) for th in thetas],
    [Vector3(r2*sin(th), r2*cos(th), z2) for th in thetas],
    [Vector3(r1*sin(th), r1*cos(th), z1) for th in thetas],
    [Vector3(r1*sin(th), r1*cos(th), zHeight) for th in thetas]
]
surf = pack.sweptPolylines2gtsSurface(meridians)
O.bodies.append(pack.gtsSurface2Facets(surf, material=matOfFunnel))

# Wall
O.bodies.append(wall(position=0, axis=2, material=matOfSphere))

# Predicate
r1 = r1 - 0.5*d90
r2 = r2 - 0.5*d90
meridians = [
    [Vector3(r2*sin(th), r2*cos(th), z3) for th in thetas],
    [Vector3(r2*sin(th), r2*cos(th), z2) for th in thetas],
    [Vector3(r1*sin(th), r1*cos(th), z1) for th in thetas],
    [Vector3(r1*sin(th), r1*cos(th), zHeight) for th in thetas]
]
closedSurf = pack.sweptPolylines2gtsSurface(meridians, threshold=1e-6, capStart=True, capEnd=True)
pred = pack.inGtsSurface(closedSurf)

# Cloud of spherical particles
sp = pack.SpherePack()
sp.makeCloud(*pred.aabb(), **theParticleDist)
sp = pack.filterSpherePack(pred, sp, returnSpherePack=True)
spIDs = sp.toSimulation(material=matOfSphere)
print(f'Added {len(sp)} particles to simulation')


# ============================================================
# SIMULATION CONTROL
# ============================================================

# PyRunner to check simulation progress
def progress():
    print(f'iter = {O.iter:<7d} : t = {O.time:.5g}')

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
    ke = kineticEnergy()
    print(f'current kinetic energy: {ke:.4e}')

    if ke < limitKE:
        print(f'simulation stopped at iteration {O.iter}')
        O.pause()

# Main simulation loop
O.engines = [
    ForceResetter(),
    InsertionSortCollider(
        [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb(), Bo1_Wall_Aabb()]
    ),
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom(), Ig2_Wall_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_MindlinPhys(**theMatFunctor)],
        [Law2_ScGeom_MindlinPhys_Mindlin(includeAdhesion=True)]
    ),
    NewtonIntegrator(gravity=gravity),
    VTKRecorder(iterPeriod=10000, fileName=os.path.join(outputTmp, "p1-"), recorders=['spheres', 'facets']),
    PyRunner(command="progress()", iterPeriod=1000),
    PyRunner(command='addPlotData()', iterPeriod=500),
    PyRunner(command='checkKinetic()', iterPeriod=10000)
]

# Stopping criterion based on average velocity
totalMass = sum(O.bodies[i].state.mass for i in spIDs)
limitKE = 0.5 * totalMass * limitVelo ** 2
print(f'Stop simulation if kinetic energy drops below {limitKE}')

# Track energies
O.trackEnergy = True

# Define plots
plot.plots = {'t': ('coordNum', 'unForce'), 't ': (O.energy.keys, None, 'Etot')}

# Set critical timestep
O.dt = PWaveTimeStep()
print(f'Critical timestep set to {O.dt:.5e}')

# ============================================================
# SIMULATION
# ============================================================

# Run simulation
O.saveTmp()
t = default_timer()
O.run(500001, True)
print(f'Simulation took {default_timer()-t} s')

# Save results
O.save(os.path.join(outputDir, "simulation.yade"))
sp.fromSimulation()
sp.save(os.path.join(outputDir, "spherePack"))
plot.saveDataTxt(os.path.join(outputDir, "tableData"))

# Save plots to file
figs = plot.plot(subPlots=False, noShow=True)
for i, fig in enumerate(figs):
    fig.savefig(os.path.join(outputDir, f"fig{i}.pdf"))

# exit yade manually
sys.exit(0)