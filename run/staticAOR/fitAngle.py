# packages
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import logging

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
logName = os.path.join(outputDir, 'fitAngle.log')
logging.basicConfig(filename=logName, level=logging.INFO, filemode='w')


# ============================================================
# Gauss Newton
# ============================================================

class Optimizer:
    def fit(self, f, state=None, *, maxIter, eps):
        if state is None:
            state = f.initial()
        logger.info("Starting optimization")
        for i in range(maxIter):
            state, residual = self.step(f, state)
            logger.info(f"Current residual {residual:.5e}")
            if residual < eps:
                logger.info(f'terminated at iteration {i}, residual = {residual:.5g} and nEval = {f.nEval()}')
                return state
        logger.info('Optimizer did not reach target residual')
        return state

class GaussNewton(Optimizer):
    def step(self, f, state):
        b, A = f.eval(state)
        state = state + np.linalg.lstsq(A, b, rcond=None)[0].flatten()
        return state, 0.5 * np.sum(b**2)

class Objective:
    def __init__(self, X=None, y=None):
        super().__init__()
        self.__X = X
        self.__y = y
        self.__nEval = 0

    def eval(self, state):
        self.__nEval += 1
        return (
            self.__y - self.fun(self.__X, state),
            self.der(self.__X, state)
        )

    def nEval(self):
        return self.__nEval

class Cone(Objective):
    def initial(self):
        '''
            state[0] Height
            state[1] Radius
        '''
        return np.ones(2)*1e-3

    def fun(self, X, state):
        R = np.sqrt(np.sum(X**2, axis=1, keepdims=True))
        return state[0] * (1. - R/state[1])

    def der(self, X, state):
        R = np.sqrt(np.sum(X**2, axis=1, keepdims=True))
        return np.hstack((
            1. - R/state[1],
            state[0]*(1. + R/state[1]**2)
        ))

    def __call__(self, X, state):
        R = np.sqrt(np.sum(X**2, axis=1, keepdims=True))
        return np.maximum(np.zeros_like(R), state[0]*(1.0-R/state[1]))


# ============================================================
# FIT CONE
# ============================================================

# Data for Gauss Newton
M = np.loadtxt('case/postProcessing/layerHeight/0/traceSurface.dat', skiprows=2)
idx = M[:,2]>0
X = M[idx,:2]
y = M[idx,2:3]
logger.info(f"selecting {X.shape[0]} nonzero heights for optimizer")

f = Cone(X=X, y=y)
model = GaussNewton()
state = model.fit(f, maxIter=15, eps=1e-9)
angle = np.arctan(state[0]/state[1]) * 180/np.pi
logger.info(f"Final state:\nHeight {state[0]}\nRadius {state[1]}\nAngle {angle}")

# plot fitted surface
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection="3d")
ax.plot_trisurf(M[:, 0], M[:, 1], M[:, 2], linewidth=0.2, antialiased=True)
ax.plot_trisurf(M[:, 0], M[:, 1], f(M[:,:2], state).flatten(), linewidth=0.2, antialiased=True, alpha=0.5)
Lx = ax.get_xlim()[1] - ax.get_xlim()[0]
Ly = ax.get_ylim()[1] - ax.get_ylim()[0]
Lz = ax.get_zlim()[1] - ax.get_zlim()[0]
ax.set_box_aspect([1, Ly/Lx, Lz/Lx])
ax.set_axis_off()
ax.autoscale(False)
fname = os.path.join(outputDir, "cone" + "." + theImg["format"])
fig.savefig(fname, **theImg)

# exit yade
sys.exit(0)