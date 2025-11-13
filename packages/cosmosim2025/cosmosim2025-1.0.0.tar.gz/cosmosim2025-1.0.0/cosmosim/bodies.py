from dataclasses import dataclass

@dataclass
class CelestialBody:
    name: str
    mass: float
    radius: float
    position: list
    velocity: list
