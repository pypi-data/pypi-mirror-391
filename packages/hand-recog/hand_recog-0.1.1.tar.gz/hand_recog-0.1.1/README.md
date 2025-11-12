MediaPipe Hand Tracking Utility

A simple Python utility to perform hand landmark detection on static images and live webcam streams using Google's MediaPipe.

This package provides two simple functions, process_static_images and run_webcam_detection, that wrap the MediaPipe Hands solution for easy use. It is based on the official MediaPipe Hands example.

Features

Webcam Detection: Run real-time hand tracking on your default webcam feed with a single function call.

Static Image Processing: Process one or more static images, detect all hands, and save annotated copies to a specified directory.

3D Landmark Plotting: Optionally plots 3D world landmarks for each detected hand (requires matplotlib).

Installation

You can install this package directly from PyPI:

pip install your-package-name


This will also install all necessary dependencies.

Requirements

This package requires the following Python libraries:

opencv-python

mediapipe

matplotlib (for 3D landmark plotting)

Usage

Once installed, you can import the utility functions into your own Python scripts.

Example 1: Run Webcam Detection

This will open your default webcam (index 0) and start real-time hand detection. The annotated video stream will be displayed in an OpenCV window.

Press the 'ESC' key to quit.

# Import the package (assuming your file is named 'hand_tracker.py' inside the package)
from your_package_name import hand_tracker

# Run the webcam detection
hand_tracker.run_webcam_detection(camera_index=0)


Example 2: Process Static Images

This function will process a list of image files, draw hand landmarks on them, and save the new annotated images to an output directory.

from your_package_name import hand_tracker

# Create a list of image paths you want to process
image_list = [
    '/path/to/your/image1.jpg',
    '/path/to/your/image2.png'
]

# Specify an output directory
output_folder = "annotated_hand_images"

# Process the images
hand_tracker.process_static_images(image_list, output_dir=output_folder)

print(f"Processed images saved to '{output_folder}'")


This will create a folder named annotated_hand_images in your current directory and save files like annotated_image_0.png and annotated_image_1.png inside it.