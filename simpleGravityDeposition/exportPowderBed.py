# -*- encoding=utf-8 -*-

# packages
import numpy as np
import sys

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load('results/spherePack.txt')

# material name
material = "steel"

# powder layer thickness
lth = 100e-6

# write dictionary entries
with open('results/powderBedDict', 'w') as f:
    for center, radius in spherePack:
        if center[2] + radius < lth:
            f.write(
f'''
sphereToCell
{{
    centre ({center[0]} {center[1]} {center[2]});
    radius {radius};
    fieldValues
    (
        volScalarFieldValue alpha.{material} 1
    );
}}
'''
            )

# exit yade manually
sys.exit(0)
