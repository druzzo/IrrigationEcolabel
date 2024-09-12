import rasterio
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import LineString
from tkinter import Tk, filedialog, simpledialog, messagebox
import rasterio.features
from irrigation_network_efficiency import calculate_ideal_liters_per_dripper, calculate_overuse_ratio
import matplotlib.colors as mcolors
import math

def request_tif_path():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Select File",
                        "Please select the TIF file of the mask that defines the canopy (canopy values must be 1 and 'no canopy' must be 0).")
    tif_path = filedialog.askopenfilename(filetypes=[("TIF File", "*.tif"), ("All files", "*.*")])
    root.destroy()
    return tif_path

def request_vector_path():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo("Select File", "Please select the vector layer of the irrigation network.")
    vector_path = filedialog.askopenfilename(filetypes=[("SHP Files", "*.shp"), ("All files", "*.*")])
    root.destroy()
    return vector_path

def read_dem(tif_path):
    with rasterio.open(tif_path) as src:
        dem = src.read(1)  # Read the first band
        profile = src.profile
        bounds = src.bounds
    return dem, profile, bounds

def read_vector_layer(vector_path):
    return gpd.read_file(vector_path)

def show_tif_image(dem, bounds):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(dem, cmap='viridis', vmin=0, vmax=1, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    plt.colorbar(im, label='Elevation', ticks=[0, 1], ax=ax)
    ax.set_title('Canopy Height Model (CHM)')
    ax.set_xlabel('Columns')
    ax.set_ylabel('Rows')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it

def show_vector_layer(vector_layer, title):
    fig, ax = plt.subplots(figsize=(10, 8))
    vector_layer.plot(ax=ax, color='orange')
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it

def create_irrigation_network_buffer(vector_layer, width):
    buffer = vector_layer.copy()
    buffer['geometry'] = buffer.geometry.apply(lambda geom: geom.buffer(width, cap_style=2))
    return buffer

def show_buffer_outline(dem, bounds, buffer, irrigation_width):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(dem, cmap='viridis', vmin=0, vmax=1, alpha=0.7,
                    extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    buffer.boundary.plot(ax=ax, edgecolor='orange', linewidth=2)  # Draw only the outline
    plt.colorbar(im, label='Elevation', ticks=[0, 1], ax=ax)
    ax.set_title('Irrigation Network with Buffer and CHM')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.text(bounds.right - (bounds.right - bounds.left) * 0.1,
             bounds.top - (bounds.top - bounds.bottom) * 0.05,
             f'Irrigation width: {irrigation_width:.2f} m',
             horizontalalignment='right',
             color='white',
             fontsize=12,
             bbox=dict(facecolor='black', alpha=0.5))
    plt.show()
    plt.close(fig)  # Close the figure after displaying it

def calculate_lengths(vector_layer):
    vector_layer['length'] = vector_layer.geometry.length
    return vector_layer

def show_irrigation_network_with_lengths(dem, bounds, vector_layer):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(dem, cmap='viridis', vmin=0, vmax=1, alpha=0.7,
                    extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    vector_layer.plot(ax=ax, edgecolor='orange', linewidth=2)  # Draw only the outline

    for idx, row in vector_layer.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f'{row["length"]:.2f}m',
                 color='white', fontsize=8, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

    plt.colorbar(im, label='Elevation', ticks=[0, 1], ax=ax)
    ax.set_title('Irrigation Network with Lengths and CHM')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it

def calculate_mean_pixel_value(buffer, dem, bounds):
    buffer['mean_value'] = 0.0
    transform = rasterio.transform.from_bounds(bounds.left, bounds.bottom, bounds.right, bounds.top, dem.shape[1],
                                               dem.shape[0])

    for idx, row in buffer.iterrows():
        geom = row.geometry
        mask = rasterio.features.geometry_mask([geom], transform=transform, invert=True, out_shape=dem.shape)
        masked_dem = dem[mask]
        mean_value = np.mean(masked_dem[masked_dem >= 0])  # Ignore values outside the mask
        buffer.at[idx, 'mean_value'] = mean_value

    return buffer

def show_irrigation_network_with_values(dem, bounds, buffer):
    fig, ax = plt.subplots(figsize=(10, 8))

    # Display the CHM (Canopy Height Model) underneath
    im = ax.imshow(dem, cmap='viridis', vmin=0, vmax=1, alpha=0.7,
                   extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

    # Make the buffer transparent and only show the perimeter
    buffer.boundary.plot(ax=ax, edgecolor='orange', linewidth=2)  # Draw only the perimeter

    for idx, row in buffer.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f'{row["mean_value"]:.2f}',
                 color='white', fontsize=8, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

    plt.colorbar(im, label='Elevation', ticks=[0, 1], ax=ax)
    ax.set_title('Average Coverage Factor per Irrigation Line')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it

def obtain_coverage_factor_and_create_buffer(buffer_width):
    tif_path = request_tif_path()
    if not tif_path:
        messagebox.showerror("Error", "No file was selected.")
        return None, None, None

    vector_path = request_vector_path()
    if not vector_path:
        messagebox.showerror("Error", "No vector file was selected.")
        return None, None, None

    dem, profile, bounds = read_dem(tif_path)
    vector_layer = read_vector_layer(vector_path)

    show_tif_image(dem, bounds)
    show_vector_layer(vector_layer, 'Irrigation Network')

    buffer = create_irrigation_network_buffer(vector_layer, buffer_width)
    show_buffer_outline(dem, bounds, buffer, buffer_width * 2)

    buffer = calculate_mean_pixel_value(buffer, dem, bounds)
    show_irrigation_network_with_values(dem, bounds, buffer)

    coverage_factor = buffer['mean_value'].mean()  # Calculate the average coverage factor

    return coverage_factor, tif_path, vector_path, buffer

def generate_ideal_liters_per_dripper_map(buffer, liters_per_dripper, avg_fc):
    buffer['ideal_liters'] = buffer['mean_value'].apply(
        lambda fc: (liters_per_dripper / avg_fc) * fc
    )

    max_value = buffer['ideal_liters'].max()
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    cmap = plt.cm.Blues

    fig, ax = plt.subplots(figsize=(10, 8))
    buffer.plot(ax=ax, column='ideal_liters', cmap=cmap, linewidth=2, edgecolor='black', norm=norm)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm, ax=ax, ticks=range(int(max_value) + 1))
    cbar.ax.set_yticklabels([str(i) for i in range(int(max_value) + 1)])

    for idx, row in buffer.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f'{row["ideal_liters"]:.2f}',
                 color='white', fontsize=8, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

    ax.set_title('Ideal Liters per Dripper per Irrigation Line')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it
    return fig

def generate_rounded_ideal_liters_map(buffer):
    buffer['rounded_ideal_liters'] = buffer['ideal_liters'].apply(math.ceil)

    max_value = buffer['rounded_ideal_liters'].max()
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    cmap = plt.cm.Blues

    fig, ax = plt.subplots(figsize=(10, 8))
    buffer.plot(ax=ax, column='rounded_ideal_liters', cmap=cmap, linewidth=2, edgecolor='black', norm=norm)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    cbar = plt.colorbar(sm, ax=ax, ticks=range(int(max_value) + 1))
    cbar.ax.set_yticklabels([str(i) for i in range(int(max_value) + 1)])

    for idx, row in buffer.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f'{row["rounded_ideal_liters"]}',
                 color='white', fontsize=8, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

    ax.set_title('Rounded Ideal Liters to the Nearest Whole Number per Dripper per Irrigation Line')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it
    return fig

def generate_overuse_ratio_map(buffer, actual_flow):
    buffer['overuse_ratio'] = buffer['rounded_ideal_liters'].apply(
        lambda ideal_liters: calculate_overuse_ratio(actual_flow, ideal_liters)
    )

    max_value = 500  # Set the maximum value. Good ratio: 500
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    cmap = plt.cm.Reds

    fig, ax = plt.subplots(figsize=(10, 8))
    buffer.plot(ax=ax, column='overuse_ratio', cmap=cmap, linewidth=2, edgecolor='black', norm=norm)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    ticks = [0, max_value // 4, max_value // 2, 3 * max_value // 4, max_value]
    cbar = plt.colorbar(sm, ax=ax, ticks=ticks)
    cbar.ax.set_yticklabels([str(i) for i in ticks])

    for idx, row in buffer.iterrows():
        ax.text(row.geometry.centroid.x, row.geometry.centroid.y, f'{row["overuse_ratio"]:.2f}',
                 color='white', fontsize=8, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

    ax.set_title('Overuse Ratio per Irrigation Line')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()
    plt.close(fig)  # Close the figure after displaying it
    return fig

if __name__ == "__main__":
    obtain_coverage_factor_and_create_buffer()
