import tkinter as tk
from tkinter import filedialog, messagebox
import skimage.io as io
import skimage.exposure as exposure
from skimage import filters, color, morphology, measure
import numpy as np

def calculate_follicle_diameters(image_path):
    # Read the image
    image = io.imread(image_path)

    # Increase contrast
    enhanced_image = exposure.equalize_hist(image)
    # Convert to grayscale
    gray_image = color.rgb2gray(enhanced_image)

    # Apply Otsu's thresholding
    otsu_threshold = filters.threshold_otsu(gray_image)
    binary_image = gray_image > otsu_threshold

    # Perform morphology closing
    selem = morphology.disk(5)  # Define structuring element
    closed_image = morphology.binary_closing(binary_image, selem)

    # Invert the image
    inverted_image = np.logical_not(closed_image)

    # Label connected components
    label_image = measure.label(inverted_image)

    # Remove small objects based on diameter and border touching
    min_diameter_threshold = 2  # Minimum diameter threshold in mm
    min_area_threshold = np.pi * (min_diameter_threshold / 2) ** 2

    follicle_diameters = []

    for region in measure.regionprops(label_image):
        # Calculate diameter
        diameter = region.equivalent_diameter
        # Check if diameter is less than the threshold or if region touches the border
        if diameter < min_diameter_threshold or region.bbox[0] == 0 or region.bbox[1] == 0 or \
                region.bbox[2] == label_image.shape[0] or region.bbox[3] == label_image.shape[1]:
            label_image[label_image == region.label] = 0
        else:
            follicle_diameters.append(diameter)

    # Convert back to binary image
    cleaned_image = label_image > 0

    # Count the number of follicles
    num_follicles = len(follicle_diameters)

    # Determine if the result is positive or negative
    result = "Positive" if num_follicles >= 12 else "Negative"

    return follicle_diameters, num_follicles, result

def browse_image():
    # Browse image file
    image_path = filedialog.askopenfilename(title="Select Image File",
                                             filetypes=(("JPEG files", "*.jpg"), ("All files", "*.*")),
                                             initialdir="/work/ghartimagar/Bioimaging/train_small/pco")
    if image_path:
        # Calculate follicle diameters
        follicle_diameters, num_follicles, result = calculate_follicle_diameters(image_path)
        # Display results
        message = f"Follicle Diameters (mm):\n{follicle_diameters}\n\n"
        message += f"Number of Follicles: {num_follicles}\n"
        message += f"Result: {result}"
        messagebox.showinfo("Follicle Analysis", message)

# Create Tkinter application window
app = tk.Tk()
app.title("Follicle Diameter Calculator")
app.geometry("300x200")
app.config(bg="#AEC6CF")

# Add a button to browse for an image
browse_button = tk.Button(app, text="Browse Image", command=browse_image, bg="salmon")
browse_button.pack(pady=20)

# Run the Tkinter event loop
app.mainloop()
