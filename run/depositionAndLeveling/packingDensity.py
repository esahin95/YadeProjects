O.load('data/simulation.yade')

xmin, xmax = aabbExtrema()
zmin = xmin[2]

print(zmin)

lt = 0.003

totalVolume = 0
for body in O.bodies:
    if isinstance(body.shape, Sphere):
        if body.state.pos[2] < zmin + lt:
            totalVolume += body.state.mass / body.material.density
packing = totalVolume / 0.01 / lt
   
print(totalVolume, packing)

totalVolume = 0
for body in O.bodies:
    if isinstance(body.shape, Sphere):
        totalVolume += body.state.mass / body.material.density
packing = totalVolume / 0.01 / 0.02

print(totalVolume, packing)
