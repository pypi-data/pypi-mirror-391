from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easy-filters",
    version="0.1.1",  # IMPORTANT: I've updated the version to "0.1.1"
    
    author="Anisha Mhatre",         
    author_email="anisha.mhatre3@gmail.com", 
    
    # This is the short description shown on PyPI
    description="A simple Python library for real-time webcam filters",
    
    # This is the long description from your README file
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    packages=find_packages(),
    
    # Dependencies
    install_requires=[
        'numpy',
        'opencv-contrib-python'
    ],
    
    # Extra metadata
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)