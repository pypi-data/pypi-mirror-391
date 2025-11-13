from .constants import C

def doppler_shift(v_radial, wavelength):
    beta = v_radial / C
    shifted = wavelength * ((1 + beta) / (1 - beta))**0.5
    z = (shifted - wavelength) / wavelength
    return shifted, z
