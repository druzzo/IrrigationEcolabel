from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import io
import os
from PIL import Image
from tkinter import filedialog, Tk

def save_plot_to_image(fig, description):
    image_path = f"{description}.png"
    fig.savefig(image_path, format='png')
    return image_path

def add_image_to_pdf(c, image_path, page_width, page_height, margin, scale=0.7, overuse_ratio=None):
    try:
        img = Image.open(image_path)
        aspect = img.width / img.height
        max_width = page_width - 2 * margin
        max_height = page_height / 2  # Limit the height to half of the page

        if aspect > 1:
            width = min(max_width, img.width * scale)  # Scale of max width
            height = width / aspect
        else:
            height = min(max_height, img.height * scale)  # Scale of max height
            width = height * aspect

        x = (page_width - width) / 2
        y = (page_height - height) / 2  # Place the image in the middle of the page

        c.drawImage(image_path, x, y, width, height, preserveAspectRatio=True, mask='auto')

        # Add overuse ratio text above the label
        if overuse_ratio is not None:
            text_x = x + width / 2 + 50
            text_y = y + 54    # Adjust the position above the label
            c.setFont("Helvetica-Bold", 32)
            c.setFillColorRGB(0, 0, 0)  # Set text color to black
            c.drawCentredString(text_x, text_y, f"{overuse_ratio:.2f}")

        return x, y, width, height
    except IOError:
        print(f"Error: Could not open the image {image_path}")
        return None, None, None, None

def draw_frame(c, x, y, width, height):
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.rect(x, y, width, height)

def wrap_text(text, width, c):
    lines = []
    for line in text.split('\n'):
        while len(line) > 0:
            split_idx = c.breakText(line, width)
            lines.append(line[:split_idx])
            line = line[split_idx:]
    return lines

def create_cover(c, image_path, page_width, page_height, margin):
    y_position = page_height - margin - 50

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(page_width / 2, y_position, "Irrigation Efficiency Report")
    y_position -= 40
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width / 2, y_position, "FAO-56 Method and Drone Image Analysis")
    y_position -= 40
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width / 2, y_position, "Developed by:")
    y_position -= 20
    c.drawCentredString(page_width / 2, y_position, "Sergio Vélez, Raquel Martínez-Peña, João Valente Mar Ariza-Sentís, Miguel Ángel Pardo")
    y_position -= 60  # Leave some space between text and image
    try:
        img = Image.open(image_path)
        aspect = img.width / img.height
        max_width = page_width - 2 * margin
        max_height = page_height / 2  # Limit the height to half of the page
        if aspect > 1:
            img_width = min(max_width, img.width * 0.5)  # 50% of max width
            img_height = img_width / aspect
        else:
            img_height = min(max_height, img.height * 0.5)  # 50% of max height
            img_width = img_height * aspect
        x = (page_width - img_width) / 2
        y = y_position - img_height if (y_position - img_height) > margin else margin  # Ensure it doesn't go below the margin
        c.drawImage(image_path, x, y, img_width, img_height, preserveAspectRatio=True, mask='auto')
    except IOError:
        print(f"Error: Could not open the image {image_path}")
    draw_frame(c, margin, margin, page_width - 2 * margin, page_height - 2 * margin)  # Draw the frame last
    c.showPage()

def create_pdf(partial_results, final_results, cover_image_path, dem_image_path, vector_image_path, diagram_image_path, label_image_path, filename, fig_ideal_liters=None, fig_rounded_ideal_liters=None, fig_overuse_ratio=None, label_A_image_path=None, overuse_ratio=None, assigned_letter=None):
    c = canvas.Canvas(filename, pagesize=letter)
    page_width, page_height = letter
    margin = 0.5 * inch

    # Create cover
    create_cover(c, cover_image_path, page_width, page_height, margin)

    # First page with partial and final results
    y_position = page_height - margin - 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, y_position, "FAO Data Summary")
    c.setFont("Helvetica", 10)
    y_position -= 20
    text = c.beginText(margin + 10, y_position)
    for line in partial_results.split('\n'):  # Splitting text by lines
        text.textLine(line)
    c.drawText(text)
    y_position = text.getY() - 20

    y_position -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, y_position, "Irrigation Data Summary")
    c.setFont("Helvetica", 10)
    y_position -= 20
    text = c.beginText(margin + 10, y_position)
    for line in final_results.split('\n'):  # Splitting text by lines
        text.textLine(line)
    c.drawText(text)
    draw_frame(c, margin, margin, page_width - 2 * margin, page_height - 2 * margin)  # Draw the frame last
    c.showPage()

    # Add images on separate pages with description and frame
    def add_image_page(image_path, title, description, scale=0.7, overuse_ratio=None, assigned_letter=None):
        y_position = page_height - margin - 40  # Adjust starting y position

        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 10, y_position, title)
        y_position -= 20
        c.setFont("Helvetica", 10)

        # Wrap text to fit within the page margins
        wrapped_text = wrap_text(description, page_width - 2 * margin - 20, c)
        for line in wrapped_text:
            text = c.beginText(margin + 10, y_position)
            text.textLine(line)
            c.drawText(text)
            y_position -= 12  # Move down for next line

        if assigned_letter:
            y_position -= 20
            c.setFont("Helvetica", 10)
            c.drawString(margin + 10, y_position, f"The assigned letter is {assigned_letter}")

        y_position -= 20  # Add some space between text and image
        x, y, width, height = add_image_to_pdf(c, image_path, page_width, page_height, margin, scale=scale, overuse_ratio=overuse_ratio)
        draw_frame(c, margin, margin, page_width - 2 * margin, page_height - 2 * margin)  # Draw the frame last
        c.showPage()

    if dem_image_path:
        add_image_page(dem_image_path, "Canopy Height Model (CHM)", "This figure shows the Canopy Height Model (CHM) for the study area, specifically identifying areas occupied by vineyard vegetation. The different shades and heights reflect the canopy coverage, showing where the plants are within the vineyard.")
    if vector_image_path:
        add_image_page(vector_image_path, "Irrigation Network", "This figure shows the current irrigation network of the study area.")
    if diagram_image_path:
        add_image_page(diagram_image_path, "Consumption Diagram", "This diagram shows the relationships between ET0, ETc, and other variables.")
    if label_image_path:
        add_image_page(label_image_path, "Sustainability Label", "This figure shows the sustainability label of the irrigation installation, based on the result of the resource overuse ratio.", scale=0.56)

    # Add the new figures
    if fig_ideal_liters:
        fig_ideal_liters_path = save_plot_to_image(fig_ideal_liters, "ideal_liters")
        add_image_page(fig_ideal_liters_path, "Ideal Liters per Dripper Map", "This map shows the ideal liters per dripper for each irrigation line.")
    if fig_rounded_ideal_liters:
        fig_rounded_ideal_liters_path = save_plot_to_image(fig_rounded_ideal_liters, "rounded_ideal_liters")
        add_image_page(fig_rounded_ideal_liters_path, "Rounded Ideal Liters Map", "This map shows the rounded ideal liters per dripper for each irrigation line.")
    if fig_overuse_ratio:
        fig_overuse_ratio_path = save_plot_to_image(fig_overuse_ratio, "overuse_ratio")
        add_image_page(fig_overuse_ratio_path, "Overuse Ratio Map", "This map shows the overuse ratio for each irrigation line. The values are in % times more irrigation.")

    # Select the label image based on the assigned letter
    label_image_map = {
        "A+++": "images/label_A+++.jpg",
        "A++": "images/label_A++.jpg",
        "A+": "images/label_A+.jpg",
        "A": "images/label_A.jpg",
        "B": "images/label_B.jpg",
        "C": "images/label_C.jpg",
        "D": "images/label_D.jpg"
    }
    label_A_image_path = label_image_map.get(assigned_letter, "images/label_A.jpg")

    if label_A_image_path:
        add_image_page(label_A_image_path, "Efficiency label", "This figure shows the Efficiency label for this facility.", scale=0.56, overuse_ratio=overuse_ratio, assigned_letter=assigned_letter)

    try:
        c.save()
        print(f"PDF saved at: {filename}")
    except PermissionError:
        print(f"Error: Could not save the file {filename}. It is open or there is no permission.")
        new_save_path = request_new_save_path()
        if new_save_path:
            create_pdf(partial_results, final_results, cover_image_path, dem_image_path, vector_image_path, diagram_image_path, label_image_path, new_save_path, fig_ideal_liters, fig_rounded_ideal_liters, fig_overuse_ratio, label_A_image_path, overuse_ratio, assigned_letter)

def wrap_text(text, width, c):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if c.stringWidth(current_line + word) < width:
            current_line += f"{word} "
        else:
            lines.append(current_line)
            current_line = f"{word} "
    if current_line:
        lines.append(current_line)
    return lines

def request_new_save_path():
    root = Tk()
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    root.destroy()
    return save_path

def save_plots_and_create_pdf(partial_results, final_results, cover_image_path, dem=None, vector_layer=None, diagram_image=None, label_image=None, pdf_filename=None, fig_ideal_liters=None, fig_rounded_ideal_liters=None, fig_overuse_ratio=None, label_A_image_path=None, overuse_ratio=None, assigned_letter=None):
    dem_image_path = vector_image_path = None
    fig_ideal_liters_path = fig_rounded_ideal_liters_path = fig_overuse_ratio_path = None

    # Create figure for DEM
    if dem is not None:
        fig1, ax1 = plt.subplots(figsize=(10, 8))
        if hasattr(dem, 'geometry'):
            dem_values = dem.drop(columns='geometry')
        else:
            dem_values = dem
        min_val = dem_values[dem_values > -9999].min().min()
        max_val = dem_values[dem_values > -9999].max().max()
        cax1 = ax1.imshow(dem_values, cmap='viridis', vmin=min_val, vmax=max_val)
        fig1.colorbar(cax1, ax=ax1, label='Elevation')
        ax1.set_title('Canopy Height Model (CHM)')
        dem_image_path = save_plot_to_image(fig1, "dem_image")
        plt.close(fig1)

    # Create figure for vector layer
    if vector_layer is not None:
        fig2, ax2 = plt.subplots(figsize=(10, 8))
        vector_layer.plot(ax=ax2, color='orange')
        ax2.set_title('Irrigation Network')
        vector_image_path = save_plot_to_image(fig2, "vector_image")
        plt.close(fig2)

    # Save additional images
    diagram_image_path = save_plot_to_image(diagram_image, "diagram_image") if diagram_image else None
    label_image_path = save_plot_to_image(label_image, "label_image") if label_image else None

    # Save images and create PDF
    create_pdf(
        partial_results, final_results, cover_image_path, dem_image_path, vector_image_path,
        diagram_image_path, label_image_path, pdf_filename, fig_ideal_liters, fig_rounded_ideal_liters, fig_overuse_ratio, label_A_image_path, overuse_ratio, assigned_letter
    )

    # Delete temporary images
    for path in [dem_image_path, vector_image_path, diagram_image_path, label_image_path, fig_ideal_liters_path, fig_rounded_ideal_liters_path, fig_overuse_ratio_path]:
        if path:
            try:
                os.remove(path)
            except OSError as e:
                print(f"Error: Could not delete the file {path}. {e}")

