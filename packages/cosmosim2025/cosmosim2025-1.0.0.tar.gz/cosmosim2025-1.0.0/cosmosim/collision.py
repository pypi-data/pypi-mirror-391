from .bodies import CelestialBody

def collide(b1, b2):
    total_mass = b1.mass + b2.mass
    new_velocity = [(b1.velocity[i]*b1.mass + b2.velocity[i]*b2.mass)/total_mass for i in range(3)]
    new_position = [(b1.position[i] + b2.position[i])/2 for i in range(3)]
    return CelestialBody(
        name=f"{b1.name}-{b2.name}",
        mass=total_mass,
        radius=(b1.radius**3 + b2.radius**3)**(1/3),
        position=new_position,
        velocity=new_velocity
    )
