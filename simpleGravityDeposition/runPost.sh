#!/bin/bash

# export particle size distribution
yade -n checkPSD.py

# inspect results
wslview results/psd.pdf 
wslview results/fig0.pdf
wslview results/fig1.pdf

# export OpenFOAM dictionary entries
yade exportPowderBed.py

#cp results/powderBedDict ~/OpenFOAM/sahin-10/run/laserWeldNoPhaseChange/system/