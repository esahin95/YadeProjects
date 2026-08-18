# packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os 

# ============================================================
# PARAMETERS
# ============================================================

# Meters to micrometers
convertToMicrons = 1e+6

# parameters for histogram
theHist = {
    "bins":10,
    "density":True
}

# Inputs and Outputs
outputDir = "results"
theImg = {
    "dpi":300,
    "bbox_inches":"tight",
    "format":"pdf"
}

# ============================================================
# CHECK PSD
# ============================================================

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load(os.path.join(outputDir, "spherePack"))

# extract diameters
diameters = np.zeros(len(spherePack))
for i, (center, radius) in enumerate(spherePack):
    diameters[i] = 2 * radius * convertToMicrons
    
# plot histogram
plt.figure()
plt.hist(diameters, **theHist)
plt.xlabel(r'diameter in $\mu$m')
plt.savefig(os.path.join(outputDir, "psd" + "." + theImg["format"]), **theImg)
    
# exit yade
sys.exit(0)