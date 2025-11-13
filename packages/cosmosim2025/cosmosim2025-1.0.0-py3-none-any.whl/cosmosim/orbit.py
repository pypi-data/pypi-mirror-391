import math
from .constants import G

def orbital_velocity(M_central, r):
    return math.sqrt(G * M_central / r)

def orbital_period(M_central, r):
    return 2 * math.pi * math.sqrt((r**3) / (G * M_central))
