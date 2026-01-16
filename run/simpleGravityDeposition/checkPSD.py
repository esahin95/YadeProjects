# packages
import numpy as np
import matplotlib.pyplot as plt
import sys

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load('results/spherePack.txt')

# extract diameters
diameters = np.zeros(len(spherePack))
for i, (center, radius) in enumerate(spherePack):
    diameters[i] = 2 * radius * 1e+6 # scale to micrometers
    
# plot histogram
plt.figure()
plt.hist(diameters, bins=10, density=True)
plt.xlabel(r'diameter in $\mu$m')
plt.savefig('results/psd.pdf', dpi=300, bbox_inches='tight')
    
# exit yade
sys.exit(0)
