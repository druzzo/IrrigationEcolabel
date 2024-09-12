def calculate_overuse_ratio(actual_flow, ideal_liters):
    ratio = ((actual_flow - ideal_liters) / ideal_liters) * 100
    return ratio

def calculate_ideal_liters_per_dripper(fc, adjusted_nhn, irrigation_width, dripper_spacing, irrigation_efficiency, irrigation_hours):
    # Calculate the net demand per turn
    dn_turn = adjusted_nhn * fc

    # Calculate the net demand per hour of irrigation
    dn_hour = dn_turn / irrigation_hours

    # Calculate the gross water demand
    db = dn_hour / irrigation_efficiency

    # Calculate the net demand per linear meter
    dn_linear_meter = db * irrigation_width

    # Calculate liters per dripper
    liters_per_dripper = dn_linear_meter * dripper_spacing

    return liters_per_dripper
