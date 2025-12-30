# -*- encoding=utf-8 -*-

### simple gravity deposition without compaction of resulting powder bed

# import packages
from yade import plot
import numpy as np
import sys
from timeit import default_timer

# box dimensions
theBox = (1.5e-3, 0.5e-3, 0.1e-3)

# gravity
gravity = (0.0, 0.0, -9.81)

# particle distribution
theParticleDist = {"psdSizes":[40e-6, 60e-6], "psdCumm":[0.0, 1.0]}

# material parameters, scaled young modulus
theMat = {
    "young":110e+6, 
    "poisson":0.34, 
    "frictionAngle":radians(30), 
    "density":4430, 
    "label":"Ti64"
}

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
        # stop simulation and save state
        O.pause()
        O.save('results/simulation.yade')
        print(f'simulation stopped at iteration {O.iter}')

        # save powder bed
        sp.fromSimulation()
        sp.save('results/spherePack.txt')

        # save plot data as text file
        plot.saveDataTxt('results/plotData.txt')

# simulation boundary
theBoxCenter = tuple(0.5*x for x in theBox)
O.bodies.append(
    geom.facetBox(
        theBoxCenter, 
        theBoxCenter, 
        wallMask=31
    )
)

# cloud of spherical particles
sp = pack.SpherePack()
sp.makeCloud((0,0,0), theBox, **theParticleDist)
spIDs = sp.toSimulation(material=FrictMat(**theMat))
print(f'added {len(sp)} particles to simulation')    

# stopping criterion based on average velocity
limitVelo = 5e-3
totalMass = sum(O.bodies[i].state.mass for i in spIDs) 
print(f'total mass added to system is {totalMass:.5e}')
limitKE = 0.5 * totalMass * limitVelo ** 2
print(f'stop simulation if kinetic energy drops below {limitKE}')

# initialize cloud with mean falling velocity
meanVelo = np.sign(gravity[2]) * np.sqrt(np.abs(theBox[2] * gravity[2]) * 0.5)
for spID in spIDs:
    O.bodies[spID].state.vel[2] = meanVelo
print(f'particles initialized with velocity {meanVelo:.5e}')

# simulation loop
O.engines = [
    # reset forces
    ForceResetter(),

    # fast collision detection
    InsertionSortCollider(
        [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb()]
    ),

    # interaction physics
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_FrictPhys()],
        [Law2_ScGeom_FrictPhys_CundallStrack()],
    ),

    # time integration
    NewtonIntegrator(gravity = gravity),

    # logging and controls
    PyRunner(command='addPlotData()', iterPeriod=200),
    PyRunner(command='checkKinetic()', iterPeriod=10000)
]

# critical timestep
O.dt = 0.5 * PWaveTimeStep()
print(f'critical timestep set to {O.dt:.5e}')

# track energies
O.trackEnergy = True

# define plots
plot.plots = {'t': ('coordNum', 'unForce'), 't ': (O.energy.keys, None, 'Etot')}

# run simulation
t = default_timer()
O.run(1000000, True)
print(f'Simulation took {default_timer()-t} s')

# save plots to file
figs = plot.plot(subPlots=False, noShow=True)
for i, fig in enumerate(figs):
    fig.savefig(f'results/fig{i}.pdf')

# exit yade manually
sys.exit(0)
