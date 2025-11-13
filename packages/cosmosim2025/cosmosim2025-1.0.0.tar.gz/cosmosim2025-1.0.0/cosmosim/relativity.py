import math
from .constants import G, C

def perihelion_precession(M_central, a, e):
    return (6 * math.pi * G * M_central) / (a * (1 - e**2) * C**2)
