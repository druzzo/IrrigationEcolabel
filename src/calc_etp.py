import math

def calculate_et0(tmax, tmin, tmean, rs, rhmean, u2, z, lat, day_of_year):
    # Constants
    Gsc = 0.0820  # Solar constant in MJ m-2 min-1
    sigma = 4.903e-9  # Stefan-Boltzmann constant in MJ K-4 m-2 d-1

    # Step 1: Calculate Delta (slope of the saturation vapor pressure curve)
    delta = 4098 * (0.6108 * math.exp((17.27 * tmean) / (tmean + 237.3))) / (tmean + 237.3) ** 2

    # Step 2: Calculate gamma (psychrometric constant)
    p = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26  # Atmospheric pressure
    gamma = 0.000665 * p

    # Step 3: Calculate es (saturation vapor pressure)
    es = (0.6108 * math.exp((17.27 * tmax) / (tmax + 237.3)) + 0.6108 * math.exp((17.27 * tmin) / (tmin + 237.3))) / 2

    # Step 4: Calculate ea (actual vapor pressure)
    ea = es * (rhmean / 100)

    # Step 5: Calculate Rn (net radiation)
    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    sol_decl = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
    omega_s = math.acos(-math.tan(lat * math.pi / 180) * math.tan(sol_decl))
    ra = (24 * 60 / math.pi) * Gsc * dr * (
            omega_s * math.sin(lat * math.pi / 180) * math.sin(sol_decl) +
            math.cos(lat * math.pi / 180) * math.cos(sol_decl) * math.sin(omega_s))
    rso = (0.75 + 2e-5 * z) * ra
    rs_rso = rs / rso if rso != 0 else 0
    rns = (1 - 0.23) * rs
    rnl = sigma * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (0.34 - 0.14 * math.sqrt(ea)) * (
            1.35 * rs_rso - 0.35)
    rn = rns - rnl

    # Step 6: Calculate G (soil heat flux)
    g = 0  # Assumed zero for a daily calculation

    # Step 7: Calculate ET0 (reference evapotranspiration)
    et0 = (0.408 * delta * (rn - g) + gamma * (900 / (tmean + 273)) * u2 * (es - ea)) / (
                delta + gamma * (1 + 0.34 * u2))

    return et0

def calculate_etc(et0, kc):
    return et0 * kc
