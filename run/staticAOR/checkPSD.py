# packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from scipy.stats import lognorm

import logging


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

# Create/configure log file
logger = logging.getLogger(__name__)
logName = os.path.join(outputDir, 'checkPSD.log')
logging.basicConfig(filename=logName, level=logging.INFO, filemode='w')

# ============================================================
# CHECK PSD
# ============================================================

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load(os.path.join(outputDir, "spherePack"))
logger.info(f"loaded particle cloud with n = {len(spherePack)}")

# extract diameters
diameters = np.zeros(len(spherePack))
for i, (center, radius) in enumerate(spherePack):
    diameters[i] = 2*radius
pdf, psd = np.histogram(diameters, bins=20, density=True)
cdf = np.cumsum(pdf)
logger.info("computed pdf and cdf of loaded sphere pack")


# exact distribution
mu  = 0.5*(np.log(d90) + np.log(d10))
std = 0.5*(np.log(d90) - np.log(d10)) / 1.2816
rv = lognorm(s=std, scale=np.exp(mu))
D = rv.rvs(1000000)
ye, x0e = np.histogram(D, bins=20, range=(d10, d90), density=True)
ye *= 0.8

# cut-off distribution
D = D[np.logical_and(D>d10, D<d90)] # not really necessary here
y, x0 = np.histogram(D, bins=20, range=(d10, d90), density=True)
z = np.hstack((0, np.cumsum(y*(x0[1:] - x0[:-1]))))
x = 0.5*(x0[1:] + x0[:-1])
logger.info("computed pdf and cdf of cut-off log normal")

# plot histogram
fig, ax = plt.subplots(figsize=(2.596,1))
ax.stairs(pdf, psd, color='r', alpha=0.3, lw=2)
ax.stairs(ye, x0e, color='b', alpha=0.3, lw=2)
ax.plot(x, y, 'r', lw=2)
ax.plot(x, rv.pdf(x), 'b', lw=2)
ax.set_xlim(d10, d90)
ax.set_axis_off()
ymin, ymax = ax.get_ylim()
logger.info(f"y axis limits: \nymin {ymin:.5e}\nymax {ymax:.5e}")
fname = os.path.join(outputDir, "psd" + "." + theImg["format"])
fig.savefig(fname, **theImg)
logger.info(f"saved psd figure to {fname}")

fig, ax = plt.subplots(figsize=(2.596,1))
ax.plot(x0, z, 'r', lw=2)
ax.plot(x0, rv.cdf(x0), 'b', lw=2)
ax.set_xlim(d10, d90)
ax.set_ylim(0, 1)
ax.set_axis_off()
fname = os.path.join(outputDir, "cdf" + "." + theImg["format"])
fig.savefig(fname, **theImg)
logger.info(f"saved cdf figure to {fname}")

# exit yade
sys.exit(0)