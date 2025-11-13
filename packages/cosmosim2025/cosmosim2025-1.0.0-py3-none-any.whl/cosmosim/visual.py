import matplotlib.pyplot as plt

def plot_orbits(bodies):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for body in bodies:
        x, y, z = zip(*body['positions'])
        ax.plot(x, y, z, label=body['name'])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.legend()
    plt.show()
