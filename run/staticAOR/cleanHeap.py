# packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import logging
from scipy.spatial import KDTree

# ============================================================
# PARAMETERS
# ============================================================

# Inputs and Outputs
outputDir = "results"
theImg = {
    "dpi":300,
    "bbox_inches":"tight",
    "pad_inches":0,
    "format":"pdf"
}

# Create/configure log file
logger = logging.getLogger(__name__)
logName = os.path.join(outputDir, 'cleanHeap.log')
logging.basicConfig(filename=logName, level=logging.INFO, filemode='w')


# ============================================================
# IMPLEMENTATION OF DBSCAN
# ============================================================

class DBSCAN:
    def fit(self, X, minPts, r, leafsize=30):
        # Processing neighbourhoods
        kdTree = KDTree(X, leafsize=leafsize)

        # Initialize variables
        m = X.shape[0]
        cluster = np.zeros(m, dtype=int)
        C = 0

        # Loop over dataset
        for i in range(m):
            if cluster[i] > 0:
                continue

            # Index set of neighbours
            N = set(kdTree.query_ball_point(X[i], r))
            if len(N) < minPts:
                continue

            # Generate new cluster
            C += 1
            cluster[i] = C
            while len(N) > 0:
                j = N.pop()

                # Add point to cluster or ignore
                if cluster[j] > 0:
                    continue
                cluster[j] = C

                # Expand neighbourhood
                NExp = set(kdTree.query_ball_point(X[j], r))
                if len(NExp) >= minPts:
                    N = N | NExp

        # Return clustering
        return cluster.reshape(-1,1)


# ============================================================
# CLEAN HEAP
# ============================================================

# load particle cloud
spherePack = pack.SpherePack()
spherePack.load(os.path.join(outputDir, "spherePack"))

# extract data
X = np.zeros((len(spherePack), 3))
dmax = 0.0
for i, (center, radius) in enumerate(spherePack):
    X[i] = center
    dmax = max(dmax, 2*radius)

# extract clusters
model = DBSCAN()
minPts, r = 4, 1.5*dmax
cluster = model.fit(X, minPts, r).flatten()
logger.info(f"run clustering algorithm for\nminPts {minPts}\nr {r}")
counts = np.bincount(cluster)
logger.info(f'Identified clusters with particle counts\n{counts}')

# scatter plot of biggest cluster
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection="3d")
i = np.argmax(counts)
ax.scatter(X[cluster==i,0], X[cluster==i,1], X[cluster==i,2], s=5)
Lx = ax.get_xlim()[1] - ax.get_xlim()[0]
Ly = ax.get_ylim()[1] - ax.get_ylim()[0]
Lz = ax.get_zlim()[1] - ax.get_zlim()[0]
ax.set_box_aspect([1, Ly/Lx, Lz/Lx])
ax.set_axis_off()
ax.autoscale(False)
ax.scatter(X[cluster!=i,0], X[cluster!=i,1], X[cluster!=i,2], s=5)
fname = os.path.join(outputDir, "clustered" + "." + theImg["format"])
fig.savefig(fname, **theImg)

# save filtered sphere pack
idx = cluster==i
spherePack.fromList([s for i, s in enumerate(spherePack.toList()) if idx[i]])
spherePack.save(os.path.join(outputDir, "filteredSpherePack"))

# initial bounding box for OpenFOAM
xmin, xmax = spherePack.aabb()
logger.info(f'bounding box of filtered sphere pack\n{xmin} - {xmax}')
logger.info(f''' Scaled to micrometers
vertices
(
    ({xmin[0]} {xmin[1]} {xmin[2]})
    ({xmax[0]} {xmin[1]} {xmin[2]})
    ({xmax[0]} {xmax[1]} {xmin[2]})
    ({xmin[0]} {xmax[1]} {xmin[2]})
    ({xmin[0]} {xmin[1]} {xmax[2]})
    ({xmax[0]} {xmin[1]} {xmax[2]})
    ({xmax[0]} {xmax[1]} {xmax[2]})
    ({xmin[0]} {xmax[1]} {xmax[2]})
);
''')

# initial hexa mesh for OpenFOAM
N = np.zeros(3).astype(int)
N[2] = 10
N[0] = round((xmax[0]-xmin[0])/(xmax[2]-xmin[2])) * N[2]
N[1] = round((xmax[1]-xmin[1])/(xmax[2]-xmin[2])) * N[2]
logger.info(f'''
blocks
(
    hex (0 1 2 3 4 5 6 7) ({N[0]} {N[1]} {N[2]}) simpleGrading (1 1 1)
);
''')

# number of refinements needed for h <= 0.2*dmax
l0 = (xmax[2]-xmin[2])/N[2]
nRefinements = np.ceil(np.log(5*l0/dmax)/np.log(2.0))
print(l0, dmax, np.ceil(np.log(5*l0/dmax)/np.log(2.0)))
logger.info(f'number of Refinements {round(nRefinements)}')

# exit yade
sys.exit(0)