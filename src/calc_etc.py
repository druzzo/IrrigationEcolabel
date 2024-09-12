from tkinter import simpledialog, Tk

def request_input(prompt, input_type=float):
    root = Tk()
    root.withdraw()  # Hide the main window
    response = simpledialog.askstring(title="Input", prompt=prompt)
    root.destroy()
    try:
        if input_type == float:
            return float(response)
        elif input_type == int:
            return int(response)
        else:
            return response
    except ValueError:
        print(f"Error: invalid input for {prompt}")
        return None

def request_reference_etp():
    etp = request_input("Enter the ET0 value obtained from a reference station:", float)
    return etp

def perform_calculations(et0, kc, pe, au, eto_percentage):
    # ETc: Crop Evapotranspiration
    etc = et0 * kc
    # AFU: Easily Usable Water
    afu = 2 / 3 * au
    # NHN: Net Water Needs
    nhn = etc - pe
    # Adjusted NHN
    nhn_adjusted = nhn * eto_percentage
    return etc, afu, nhn, nhn_adjusted

def request_parameters():
    tmax = request_input("Enter the maximum temperature (°C):")
    tmin = request_input("Enter the minimum temperature (°C):")
    tmean = request_input("Enter the mean temperature (°C):")
    rs = request_input("Enter the solar radiation (MJ/m²/day):")
    rhmean = request_input("Enter the average relative humidity (%):")
    u2 = request_input("Enter the wind speed at 2 meters (m/s):")
    z = request_input("Enter the altitude above sea level (m):")
    lat = request_input("Enter the latitude (decimal degrees):")
    day_of_year = request_input("Enter the day of the year (1-365):", int)
    return tmax, tmin, tmean, rs, rhmean, u2, z, lat, day_of_year
