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

def request_irrigation_turn():
    return request_input("Enter the irrigation turn time (daily = 1, weekly = 7, biweekly = 14):", int)

def request_irrigation_hours():
    return request_input("Enter the number of irrigation hours per day:", float)

def request_irrigation_efficiency():
    return request_input("Enter the irrigation system efficiency (suggestion for drip irrigation: 0.9):", float)

def calculate_irrigation_need(adjusted_nhn, irrigation_turn):
    return adjusted_nhn * irrigation_turn

def calculate_net_demand_per_turn(adjusted_nhn, fc, irrigation_turn):
    # Apply the coverage factor and the irrigation turn to the calculation of the net demand per turn
    return adjusted_nhn * fc * irrigation_turn

def calculate_net_demand_per_hour(dn_turn, irrigation_hours):
    # Divide the net demand per turn by the irrigation hours to obtain the net demand per hour
    return dn_turn / irrigation_hours

def calculate_gross_demand(dn, irrigation_efficiency):
    return dn / irrigation_efficiency

def request_dripper_flow():
    return request_input("Current irrigation installation data\nEnter the dripper flow in L/h:", float)

def request_dripper_spacing():
    return request_input("Current irrigation installation data\nEnter the distance between drippers (suggestion in vineyard: 0.75 m):", float)

def request_effective_irrigation_width():
    return request_input("Current irrigation installation data\nEnter the effective irrigation width of the dripper in meters (suggestion: 1.5m):", float)
