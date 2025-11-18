# easy-filters

A simple Python library to apply fun, real-time filters to your webcam feed using OpenCV.

## Installation

Install the package from PyPI:

```bash
pip install easy-filters




#How to Use

You can import the run_webcam function into your own Python script to start the webcam feed with a filter applied.

Example
To run the default cartoon filter, create a Python file (e.g., test.py) and add the following:

from easy_filters import run_webcam

# This will run the default "cartoon" filter
run_webcam()

# Press 'q' to quit the webcam window




#Running Other Filters

You can easily specify which filter to use by passing its name to the run_webcam function:

from easy_filters import run_webcam

# Run the "oil" filter
run_webcam("oil")

# Run the "sepia" filter
run_webcam("sepia")


Available Filters

"cartoon" (default)

"edge"

"oil"

"sepia"