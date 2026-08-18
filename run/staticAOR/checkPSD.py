# packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from scipy.stats import lognorm

# ============================================================
# PARAMETERS
# ============================================================

# Powder parameters
d10 = 70e-6 # 15e-6
d90 = 80e-6 # 45e-6

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
    diameters[i] = 2*radius
pdf, psd = np.histogram(diameters, bins=20, density=True)
cdf = np.cumsum(pdf)


# exact distribution
mu  = 0.5*(np.log(d90) + np.log(d10))
std = 0.5*(np.log(d90) - np.log(d10)) / 1.2816
rv = lognorm(s=std, scale=np.exp(mu))

# cut-off distribution
D = rv.rvs(1000000)
ye, x0e = np.histogram(D, bins=30, range=(d10, d90), density=True)
ye *= 0.8
D = D[np.logical_and(D>d10, D<d90)]
y, x0 = np.histogram(D, bins=30, range=(d10, d90), density=True)
z = np.hstack((0, np.cumsum(y*(x0[1:] - x0[:-1]))))
x = 0.5*(x0[1:] + x0[:-1])

# plot histogram
plt.figure()
plt.stairs(pdf, psd, color='r', alpha=0.3)
plt.stairs(ye, x0e, color='b', alpha=0.3)
plt.plot(x, y, 'r', lw=2)
plt.plot(x, rv.pdf(x), 'b', lw=2)
plt.savefig(os.path.join(outputDir, "psd" + "." + theImg["format"]), **theImg)

plt.figure()
#plt.hist(cdf, psd, color='r', alpha=0.3)
plt.plot(x0, z, 'r', lw=2)
plt.plot(x0, rv.cdf(x0), 'b', lw=2)
#plt.set_ylim([0, 1])
plt.savefig(os.path.join(outputDir, "cdf" + "." + theImg["format"]), **theImg)

# exit yade
sys.exit(0)