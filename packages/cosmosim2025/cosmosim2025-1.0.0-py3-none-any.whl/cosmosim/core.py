from .constants import G

def gravitational_force(m1, m2, r):
    return G * m1 * m2 / (r ** 2)

def kinetic_energy(m, v):
    return 0.5 * m * (v ** 2)

def potential_energy(m1, m2, r):
    return -G * m1 * m2 / r
