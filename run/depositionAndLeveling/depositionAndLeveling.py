# -*- encoding=utf-8 -*-

# simple gravity deposition without compaction of resulting powder bed
# creating animation requires mencoder. install with "sudo apt install mencoder"
# ------------------------------------------------------------------------------------

# import packages
import matplotlib.pyplot as plt
from yade import plot, qt, ymport

# parameters -------------------------------------------------------------------------
# physical quantities are in cgs units: cm, g, s

# box dimensions
#theBox = (0.2, 0.1, 0.04)

# gravity
grav = (0.0, 0.0, -981.0)

# rake volocity
velo = (10.0, 0.0, 0.0)

# particle distribution
thePrtDist = {"psdSizes":[0.002, 0.006], "psdCumm":[0., 1.]}

# material parameters
scl = 1e-6 # scaling to increase critical timestep
theMat = {"young":1.1e+12 * scl, "poisson":0.25, "frictionAngle":0.3, "density":4.43, "label":"Ti64"}

# results directory
dname = 'data/'

# ------------------------------------------------------------------------------------


# PyRunner function definitions ------------------------------------------------------

def addPlotData():
    '''
    add data to plot. Maps time to average interactions, unbalanced force and energies
    '''
    plot.addData(t = O.time, coordNum = avgNumInteractions(), unForce = unbalancedForce(), Etot = O.energy.total(), **O.energy)

def eraseParticles():
    '''
    erase spheres that leave the domain boundary as defined by lCorner and uCorner
    '''
    for bID in sphereIDs:
        p = O.bodies[bID].state.pos
        if p[0] > uCorner[0] or p[2] < lCorner[2]:
            O.bodies.erase(bID)
            sphereIDs.remove(bID)

def checkKinetic():
    '''
    check kinetic energy as stopping criterion
    '''
    # current kinetic energy
    ke = kineticEnergy()
    print(f'current kinetic energy: {ke:.4e}')
    
    # start rake motion after deposition completed (hard coded threshold for now)
    if ke < 1e-4:
        print(f'start rake motion at iteration {O.iter}')
        simControl.command = 'checkRakePos()'
        
        # set rake velocity
        for body in [O.bodies[bID] for bID in rakeIDs]: 
            body.state.vel = Vector3(*velo)  
        
def checkRakePos():
    '''
    stop rake at final position
    '''
    # rake front position
    frontPos = max([O.bodies[bID].state.pos[0] for bID in rakeIDs])
    
    if frontPos > uCorner[0]:
        print(f'stopped at iteration {O.iter}')
        simControl.command = 'checkFinal()'
        
        # stop rake
        for body in [O.bodies[bID] for bID in rakeIDs]: 
            body.state.vel = Vector3(0.0, 0.0, 0.0) 
        
def checkFinal():
    '''
    pause simulation after particles settle down completely
    '''
    # current kinetic energy
    ke = kineticEnergy()
    print(f'current kinetic energy: {ke:.4e}')
    
    # start rake motion after deposition completed (hard coded threshold for now)
    if ke < 1e-6:
        print(f'paused simulation at iteration {O.iter}')
        O.pause()
        
        # final packing 
        sp.fromSimulation()
        sp.save(dname + 'spherePack.txt')
        
        # save plot data
        plot.saveDataTxt(dname + 'plotData.txt')  
        
        # save simulation 
        O.save(dname + 'simulation.yade')
    
# ------------------------------------------------------------------------------------


# scene construction -----------------------------------------------------------------
# randomly placed spheres in a powder container

# single material for all bodies
O.materials.append(FrictMat(**theMat))

# load container from stl
containerIDs = O.bodies.append(ymport.stl('LevelingSystem/LevelingSystem - bed.stl', wire=False, color=Vector3(0.4,0.4,0.4)))

# load rake from stl
rake = ymport.stl('LevelingSystem/LevelingSystem - rake.stl', wire=False, color=Vector3(0.6,0.2,0.2))
rakeIDs = O.bodies.append(rake)

# creating the open box
lCorner = Vector3(-0.1, 0.0, -0.05); uCorner = Vector3(0.2, 0.1, 0.1)
boxIDs = O.bodies.append(geom.facetBox(0.5*(uCorner + lCorner), 0.5*(uCorner - lCorner), wallMask=12))

# create cloud of spheres
sp = pack.SpherePack()
sp.makeCloud((-0.05, 0.0, 0.0), (0.15, 0.1, 0.04), **thePrtDist)
sphereIDs = sp.toSimulation()

# define simulation loop
O.engines = [
    # reset forces
    ForceResetter(),
    
    # approximate collision detection 
    InsertionSortCollider(
        [Bo1_Sphere_Aabb(), Bo1_Facet_Aabb()]
    ),
    
    # interactions
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(), Ig2_Facet_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_FrictPhys()],
        [Law2_ScGeom_FrictPhys_CundallStrack()],
    ),
    
    # update Positions using Newton equations
    NewtonIntegrator(gravity = grav),
    
    # save data for paraview
    VTKRecorder(fileName=dname + 'vtk/3d-', recorders=['all'], iterPeriod=400),
    
    # add custom simulation controls
    PyRunner(command = 'addPlotData()', iterPeriod=100),
    PyRunner(command = 'eraseParticles()', iterPeriod=100),
    PyRunner(command = 'checkKinetic()', iterPeriod=1000, label='simControl')
]

# set timestep
O.dt = .5 * PWaveTimeStep()

# track energy 
O.trackEnergy = True

# ------------------------------------------------------------------------------------


# run simulation ---------------------------------------------------------------------

# open view
qt.View()

# create runtime plots
plot.plots = {'t': ('coordNum', 'unForce'), 't ': (O.energy.keys, None, 'Etot')}
figs = plot.plot(subPlots=False)

# start simulation
O.run(100000)

# ------------------------------------------------------------------------------------
