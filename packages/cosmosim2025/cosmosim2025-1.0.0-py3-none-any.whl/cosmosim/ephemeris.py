import math
from .constants import AU

def earth_position(days_since_epoch):
    T = 365.25
    angle = 2 * math.pi * (days_since_epoch % T) / T
    x = AU * math.cos(angle)
    y = AU * math.sin(angle)
    return [x, y, 0]

def mars_position(days_since_epoch):
    T = 687
    angle = 2 * math.pi * (days_since_epoch % T) / T
    x = 1.524 * AU * math.cos(angle)
    y = 1.524 * AU * math.sin(angle)
    return [x, y, 0]
