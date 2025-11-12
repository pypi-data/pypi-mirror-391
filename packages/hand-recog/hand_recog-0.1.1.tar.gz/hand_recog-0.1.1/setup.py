from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='hand_recog',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'mediapipe>=0.8.9',
        'opencv-python>=4.5.0'],
    description='A package for hand recognition using MediaPipe and OpenCV',
    long_description=description,
    long_description_content_type='text/markdown',
)