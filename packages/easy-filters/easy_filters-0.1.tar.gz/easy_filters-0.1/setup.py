from setuptools import setup, find_packages

setup(
    name="easy-filters",  # The name your package will have on PyPI
    version="0.1",      # The first version
    packages=find_packages(), # This will find your 'easy_filters' folder
    
    # This is critical for your code to work!
    # It tells pip to install the libraries your code depends on.
    install_requires=[
        'numpy',              # Used in sepia_filter
        'opencv-contrib-python' # Needed for cv2 and cv2.xphoto.oilPainting
    ],
)