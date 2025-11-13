"""
test_all.py
測試 cosmosim 模組各功能是否正常
"""

from datetime import datetime
from cosmosim.earth_sun_orbit import earth_position, distance_to_sun
from cosmosim.galaxy_redshift import redshift_from_velocity, distance_from_redshift
from cosmosim.asteroid_collision import elastic_collision, kinetic_energy, orbital_change

def test_earth():
    now = datetime.utcnow()
    pos = earth_position(now)
    dist = distance_to_sun(now)
    print("🌍 Earth position (km):", pos)
    print("☀️ Distance to Sun (km):", dist)

def test_galaxy():
    z = redshift_from_velocity(21000)
    d = distance_from_redshift(z)
    print("🌌 Redshift z =", z)
    print("📏 Distance (Mpc) =", d)

def test_collision():
    v1f, v2f = elastic_collision(2e12, 5e3, 3e12, -2e3)
    e1 = kinetic_energy(2e12, v1f)
    new_orbit = orbital_change(5e3, v1f, 1.2e8)
    print("☄️ After collision velocities:", v1f, v2f)
    print("⚡ Kinetic energy:", e1)
    print("🪐 New orbit radius:", new_orbit)

if __name__ == "__main__":
    print("🔭 Running cosmosim test suite...\n")
    test_earth()
    print("\n")
    test_galaxy()
    print("\n")
    test_collision()
