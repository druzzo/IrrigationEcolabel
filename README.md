# Irrigation Eco Label - Calculation Software

## Overview
This software calculates the energy label of an irrigation installation using the FAO-56 method and drone images taken at the time of maximum vegetation development. It is designed to help users determine the efficiency and water needs of their irrigation systems. The software was developed by Sergio Vélez, Raquel Martínez-Peña, Joao Valente, Mar Ariza-Sentís, and Miguel Ángel Pardo.

## Features
- Calculates reference evapotranspiration (ET0) and crop evapotranspiration (ETc) using the FAO-56 method.
- Integrates drone imagery to determine the canopy cover factor (CC).
- Provides detailed summaries of evapotranspiration and irrigation data.
- Generates consumption diagrams and sustainability labels (Irrigation Ecolabel), based on the ROR (Resource Overutilization Ratio).
- Creates PDF reports with all the calculations, diagrams, and maps.

## Installation
To run this software, you need to have Python installed on your system along with the following libraries:
- `tkinter` (on Windows systems it is not necessary)
- `math`
- `matplotlib`
- `networkx`
- `re`
- `rasterio`
- `numpy`
- `geopandas`
- `shapely`
- `PIL`
- `reportlab`

You can install the required libraries using pip:
```bash
pip install tkinter math matplotlib networkx re rasterio numpy geopandas shapely pillow reportlab
```

## Usage
1. **Start the Software:**
   Run the `main.py` script to start the software.

2. **Input Parameters:**
   The software will prompt you to enter various parameters such as maximum temperature, minimum temperature, mean temperature, solar radiation, average relative humidity, wind speed at 2 meters, altitude, latitude, and day of the year.

3. **Choose Calculation Method for ET0:**
   You can either calculate ET0 manually by entering the required data or use the ET0 value obtained from a reference station. **Note:** ET0 should be calculated during the worst time of water consumption for the crop, usually at the moment of maximum vegetation development, but this depends on the crop.

4. **Canopy Cover (CC):**
   You have the option to enter the CC factor manually or calculate it using drone data.

5. **Input Crop Coefficient (Kc) and Other Parameters:**
   Enter the crop coefficient, effective precipitation (Peff), Available Water (AW), and percentage of ET0 to irrigate.

6. **Current Irrigation Data:**
   Enter details of your current irrigation system, including dripper flow, dripper spacing, and effective irrigation width.

7. **Generate and View Results:**
   The software will calculate and display the results, including the ET0, ETc, net irrigation needs, and other parameters. It will also generate diagrams and sustainability labels.

8. **Generate PDF Report:**
   If desired, the software can generate a PDF report containing all the calculations, diagrams, and maps. You will be prompted to save the PDF to a specified location.

## Detailed Code Explanation

### calc_etc.py
Handles user input for evapotranspiration calculations and performs various calculations related to crop evapotranspiration, readily available water, and net irrigation needs.

### calc_etp.py
Contains the function to calculate reference evapotranspiration (ET0) using the FAO-56 method.

### current_irrigation_network.py
Handles user input for current irrigation system parameters and performs calculations related to irrigation needs, net demand per turn, and net demand per hour.

### diagrams.py
Generates diagrams illustrating the relationships between different parameters such as ET0, ETc, and net water needs.

### gis.py
Handles GIS-related operations, including reading DEM files, vector layers, and creating irrigation network buffers. It also generates maps showing canopy height models and irrigation networks.

### irrigation_network_efficiency.py
Calculates the overuse ratio and ideal liters per dripper based on various input parameters.

### main.py
The main script that integrates all the modules and provides a user interface to enter parameters, perform calculations, generate diagrams, and create PDF reports.

### pdf_creator.py
Generates a PDF report containing all the calculated data, diagrams, and maps. It includes functions to save plots as images and add them to the PDF.

### ratio_label.py
Generates the sustainability label based on the overuse ratio of resources.

## Example Usage
Main.py is located in the _**src**_ folder. To run the main script, go to the _**root**_ location where your project is stored and execute _**main.py**_:
```bash
python src/main.py
```
or, alternatively, go directly to the _**src**_ folder and execute _**main.py**_:
```bash
python main.py
```

Follow the on-screen prompts to enter the required data and generate the results. The software will guide you through each step, and you can choose to generate a PDF report at the end.
If you do not have the necessary GIS data but want to see how the software works, GIS data have been added in the "GISdataExample" folder for practice. 

## Video Tutorial
A video tutorial can be found at: https://youtu.be/24AWkNPNHOA

## Authors
- Sergio Vélez
- Raquel Martínez-Peña
- Joao Valente
- Mar Ariza-Sentís
- Miguel Ángel Pardo

For any questions or support, please contact the authors:
https://github.com/druzzo/IrrigationEcolabel/
