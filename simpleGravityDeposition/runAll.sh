#!/bin/bash

# run simulation
yade -n -j 6 simpleGravityDeposition.py

# export particle size distribution
#yade -n checkPSD.py

# inspect results
#wslview results/psd.pdf 
wslview results/fig0.pdf

# export OpenFOAM dictionary entries
yade -n exportPowderBed.py

#cp results/powderBedDict ~/OpenFOAM/sahin-10/run/laserWeldNoPhaseChange/system/
