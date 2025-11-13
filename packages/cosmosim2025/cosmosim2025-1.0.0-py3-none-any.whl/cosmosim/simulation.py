import math
from .constants import G

def simulate_step(bodies, dt):
    forces = {b.name: [0, 0, 0] for b in bodies}
    for i, b1 in enumerate(bodies):
        for j, b2 in enumerate(bodies):
            if i == j: continue
            dx, dy, dz = b2.position[0]-b1.position[0], b2.position[1]-b1.position[1], b2.position[2]-b1.position[2]
            r = math.sqrt(dx**2 + dy**2 + dz**2)
            F = G * b1.mass * b2.mass / r**2
            fx, fy, fz = F*dx/r, F*dy/r, F*dz/r
            forces[b1.name][0] += fx
            forces[b1.name][1] += fy
            forces[b1.name][2] += fz
    for b in bodies:
        fx, fy, fz = forces[b.name]
        ax, ay, az = fx/b.mass, fy/b.mass, fz/b.mass
        b.velocity[0] += ax * dt
        b.velocity[1] += ay * dt
        b.velocity[2] += az * dt
        b.position[0] += b.velocity[0] * dt
        b.position[1] += b.velocity[1] * dt
        b.position[2] += b.velocity[2] * dt
