import os
import sys
import webbrowser
import numpy as np
from calc_etc import request_reference_etp, perform_calculations, request_parameters
from calc_etp import calculate_et0
from current_irrigation_network import (
    calculate_irrigation_need,
    request_irrigation_turn,
    calculate_net_demand_per_turn,
    calculate_net_demand_per_hour,
    request_irrigation_hours,
    calculate_gross_demand,
    request_irrigation_efficiency
)
from irrigation_network_efficiency import calculate_overuse_ratio
from diagrams import create_diagram
from ratio_label import plot_label
import matplotlib.pyplot as plt
from tkinter import simpledialog, Tk, messagebox, filedialog, Label, Button, Toplevel, Text, Scrollbar, END
from PIL import Image, ImageTk
import gis
import pdf_creator


def resource_path(relative_path):
    """
    Get absolute path to resource, works for development, PyInstaller, and for different systems
    """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not running in a PyInstaller bundle, set the base path to the script's location
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)

def center_window(window):
    window.update_idletasks()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_right = int(window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(window.winfo_screenheight() / 2 - window_height / 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    window.attributes("-topmost", True)
    window.focus_force()


def request_input(prompt, input_type=float):
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    response = simpledialog.askstring(title="Input", prompt=prompt, parent=root)
    root.destroy()
    if response is None:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", "No value was entered. The operation has been canceled.", parent=root)
        root.destroy()
        raise SystemExit()
    try:
        if input_type == float:
            return float(response)
        elif input_type == int:
            return int(response)
        else:
            return response
    except ValueError:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", "Invalid input. Please try again.", parent=root)
        root.destroy()
        return request_input(prompt, input_type)


def request_save_path():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    root.destroy()
    return save_path


def confirm_generate_pdf():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    response = messagebox.askyesno("Generate PDF Report", "Do you want to generate a PDF report?", parent=root)
    root.destroy()
    return response


def load_image(file_name):
    file_path = resource_path(file_name)
    if os.path.exists(file_path):
        image = Image.open(file_path)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    else:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", f"Image not found: {file_path}", parent=root)
        root.destroy()
        return None

def show_start_message():
    root = Tk()
    root.withdraw()
    root.title("Software Start")

    message = ("This is a software to calculate the energy label of the irrigation installation "
               "using the FAO-56 Penman-Monteith method and drone images taken at the time of maximum vegetation development "
               "(the most unfavorable in terms of transpiration).\n\n"
               "Software developed by Sergio Vélez, Raquel Martínez-Peña, Joao Valente, Mar Ariza-Sentís, and Miguel Ángel Pardo.")

    lbl_message = Label(root, text=message, wraplength=400, justify="center", anchor="center")
    lbl_message.pack(pady=10)

    image_tk = load_image("images/kawaii_water_drop.jpg")  # resource_path
    if image_tk:
        lbl_image = Label(root, image=image_tk)
        lbl_image.image = image_tk
        lbl_image.pack(pady=10)

    btn_ok = Button(root, text="OK", command=root.destroy, padx=10, pady=5)
    btn_ok.pack(pady=10)

    root.update_idletasks()
    center_window(root)
    root.deiconify()
    root.mainloop()

def show_end_message():
    root = Tk()
    root.withdraw()
    root.title("Thank you for using our software")

    message = "Thank you for using our software!"
    lbl_message = Label(root, text=message, wraplength=400, justify="center", anchor="center")
    lbl_message.pack(pady=10)

    image_tk = load_image("images/kawaii_water_drop.jpg")  # resource_path is used here
    if image_tk:
        lbl_image = Label(root, image=image_tk)
        lbl_image.pack(pady=10)

    btn_ok = Button(root, text="OK", command=root.destroy, padx=10, pady=5)
    btn_ok.pack(pady=10)

    root.update_idletasks()
    center_window(root)
    root.deiconify()
    root.mainloop()

def display_readme():
    readme_path = os.path.join(os.getcwd(), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as file:
            readme_content = file.read()

        readme_window = Toplevel()
        readme_window.title("README")
        readme_window.geometry("600x700")

        text_widget = Text(readme_window, wrap='word')
        text_widget.insert(END, readme_content)
        text_widget.config(state='disabled')

        scrollbar = Scrollbar(readme_window, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        center_window(readme_window)
    else:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", "The README.md file was not found in the working directory.", parent=root)
        root.destroy()

def consult_manual():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    response = messagebox.askyesno("Consult Manual", "Do you want to consult the manual (README)?", parent=root)
    root.destroy()
    if response:
        webbrowser.open("https://github.com/druzzo/WaterRatioLabel/")

def main():
    show_start_message()

    consult_manual()

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Start",
                        "Reference Evapotranspiration (ET0) and Crop Evapotranspiration (ETc) Calculator - FAO-56 Method",
                        parent=root)
    root.destroy()

    # Request current irrigation installation data
    dripper_flow = request_input("Current irrigation installation data\nEnter the dripper flow in L/h:", float)
    dripper_spacing = request_input(
        "Current irrigation installation data\nEnter the distance between drippers (suggestion in vineyard: 0.75 m):",
        float)
    irrigation_width = request_input(
        "Current irrigation installation data\nEnter the effective irrigation width of the dripper in meters (suggestion in vineyard: 1.5 m):",
        float)

    # Calculate the buffer width as half the total irrigation width
    buffer_width = irrigation_width / 2

    # Corrected prompt for ET0 calculation method
    option = request_input(
        "Do you want to enter the data to calculate ET0 manually (1) or enter the ET0 value obtained from a reference station (2)? Enter 1 or 2:",
        int)

    if option == 1:
        tmax, tmin, tmean, rs, rhmean, u2, z, lat, day_of_year = request_parameters()
        et0 = calculate_et0(tmax, tmin, tmean, rs, rhmean, u2, z, lat, day_of_year)
    elif option == 2:
        et0 = request_reference_etp()
    else:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", "Invalid option. Please try again.", parent=root)
        root.destroy()
        return

    # Request crop coefficient Kc
    kc = request_input("Enter the crop coefficient Kc (suggestion for vineyard: 0.7):")

    # Ask if you want to enter the coverage factor FC manually or calculate it
    fc_option = request_input(
        "Do you want to enter the Canopy Cover CC manually (1) or calculate it using drone data (2)? Enter 1 or 2:",
        int)

    if fc_option == 1:
        fc = request_input("Enter the Canopy Cover CC (suggestion for vineyard: 0.5):")
        tif_path, vector_path, buffer = None, None, None
    elif fc_option == 2:
        coverage_factor, tif_path, vector_path, buffer = gis.obtain_coverage_factor_and_create_buffer(buffer_width)
        if coverage_factor is None or tif_path is None or vector_path is None:
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showerror("Error", "Could not obtain coverage factor or GIS paths.", parent=root)
            root.destroy()
            return
        fc = coverage_factor
    else:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("Error", "Invalid option. Please try again.", parent=root)
        root.destroy()
        return

    pe = request_input("Enter the Effective Precipitation Peff (suggestion: 0):")
    au = request_input("Enter the value of Available Water AW (suggestion most unfavorable: 0):")

    etc, afu, nhn, _ = perform_calculations(et0, kc, pe, au, 1.0)
    eto_percentage = request_input("Enter the % of ET0 to irrigate (enter 1.0 for 100%. vineyard suggestion: 0.3):")
    nhn_adjusted = nhn * eto_percentage

    # Show FAO data summary
    fao_data_summary = (
        f"ET0 (Reference Evapotranspiration): {et0:.2f} mm/day\n"
        f"ETc (Crop Evapotranspiration): {etc:.2f} mm/day\n"
        f"Kc (Crop Coefficient): {kc:.2f}\n"
        f"CC (Canopy Cover): {fc:.2f}\n"
        f"Peff (Effective Precipitation): {pe:.2f} mm/day\n"
        f"AW (Available Water): {au:.2f} mm\n"
        f"RAW (Readily Available Water, 2/3 of AW): {afu:.2f} mm\n"
        f"NIWR (Net Irrigation Water Requirement): {nhn:.2f} mm/day\n"
        f"NIWR adjusted (deficit irrigation as % ET0): {nhn_adjusted:.2f} mm/day\n"
    )
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("FAO-56 Penman-Monteith Data Summary", fao_data_summary, parent=root)
    root.destroy()

    # Request irrigation turn and calculate the irrigation need
    irrigation_turn = request_irrigation_turn()
    irrigation_need = calculate_irrigation_need(nhn_adjusted, irrigation_turn)

    # Calculate the net water demand per irrigation turn
    dn_turn = calculate_net_demand_per_turn(nhn_adjusted, fc, irrigation_turn)

    # Request irrigation hours per day
    irrigation_hours = request_irrigation_hours()

    # Calculate the net water demand per hour of irrigation using the coverage factor FC
    dn_hour = calculate_net_demand_per_hour(dn_turn, irrigation_hours)

    # Request irrigation system efficiency
    irrigation_efficiency = request_irrigation_efficiency()

    # Calculate the gross water demand
    gross_demand = calculate_gross_demand(dn_hour, irrigation_efficiency)

    # Calculate the net demand per linear meter
    dn_linear_meter = gross_demand * irrigation_width

    # Calculate liters per dripper
    liters_per_dripper = dn_linear_meter * dripper_spacing

    # Calculate rounded liters per dripper
    rounded_liters_per_dripper = np.ceil(liters_per_dripper)

    # Calculate the overuse ratio of resources
    overuse_ratio = calculate_overuse_ratio(dripper_flow, liters_per_dripper)

    # Show irrigation data summary
    irrigation_data_summary = (
        f"The irrigation need for an interval of {irrigation_turn} day(s) is: {irrigation_need:.2f} mm/{irrigation_turn} day(s)\n"
        f"NIWR adjusted per irrigation interval: {dn_turn:.2f} l/(m2*{irrigation_turn} days)\n"
        f"NIWR adjusted per irrigation hours: {dn_hour:.2f} l/(h*m2)\n"
        f"GIWR (Gross Irrigation Water Requirement) during {irrigation_hours} hours of irrigation: {gross_demand:.2f} l/(h*m2)\n"
        f"Ideal liters per dripper: {liters_per_dripper:.2f} l/(h)\n"
        f"Rounded ideal liters per dripper: {rounded_liters_per_dripper:.2f} l/(h)\n"
        f"Real dripper flow rate: {dripper_flow:.2f} L/h\n"
        f"CC (Canopy Cover): {fc:.2f}\n"
        f"Effective irrigation width of the dripper: {irrigation_width:.2f} m\n"
        f"Buffer width: {buffer_width:.2f} m\n"
        f"Irrigation hours per interval: {irrigation_hours}\n"
        f"Distance between drippers: {dripper_spacing:.2f} m\n"
    )
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Irrigation Data Summary", irrigation_data_summary, parent=root)
    root.destroy()

    # Create the diagram with the calculated values
    fig1, ax1 = create_diagram(et0, etc, nhn, nhn_adjusted, irrigation_need, dn_turn, dn_hour, gross_demand,
                               irrigation_turn,
                               liters_per_dripper)

    # Create the label with the overuse ratio value and get the assigned letter
    fig2, ax2, assigned_letter = plot_label(overuse_ratio)

    # Display both charts simultaneously
    plt.show()

    # Generate the new map if GIS maps have been entered
    fig_ideal_liters, fig_rounded_ideal_liters, fig_overuse_ratio = None, None, None
    if fc_option == 2 and tif_path and vector_path:
        fig_ideal_liters = gis.generate_ideal_liters_per_dripper_map(buffer, liters_per_dripper, fc)
        fig_rounded_ideal_liters = gis.generate_rounded_ideal_liters_map(buffer)
        fig_overuse_ratio = gis.generate_overuse_ratio_map(buffer, dripper_flow)

    # Confirm if you want to generate the PDF
    if confirm_generate_pdf():
        while True:
            try:
                root = Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                messagebox.showinfo("Generate PDF Report",
                                    "Please indicate the path where the PDF report should be saved", parent=root)
                root.destroy()

                # Request save path for the PDF
                save_path = request_save_path()
                print(f"PDF save path: {save_path}")
                if not save_path:
                    root = Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    messagebox.showerror("Error", "No valid path was selected to save the PDF.", parent=root)
                    root.destroy()
                    return

                # Create PDF with the results and charts
                print("Saving PDF...")
                dem_data = gis.read_dem(tif_path)[0] if tif_path else None
                vector_data = gis.read_vector_layer(vector_path) if vector_path else None

                pdf_creator.save_plots_and_create_pdf(
                    fao_data_summary, irrigation_data_summary, "images/kawaii_water_drop.jpg",
                    dem_data, vector_data, fig1, fig2, save_path,
                    fig_ideal_liters, fig_rounded_ideal_liters, fig_overuse_ratio,
                    label_A_image_path="images/label_A.jpg",
                    overuse_ratio=overuse_ratio,
                    assigned_letter=assigned_letter
                )
                webbrowser.open(save_path)
                print("PDF saved and opened.")
                break
            except PermissionError:
                root = Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                messagebox.showerror("Error",
                                     "The PDF could not be saved. The file is open or there is no permission to write to the selected location.",
                                     parent=root)
                root.destroy()
                continue
    else:
        print("The PDF report will not be generated.")

    show_end_message()


if __name__ == "__main__":
    main()
