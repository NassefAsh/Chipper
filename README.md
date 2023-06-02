# Chipper

Note: This tool is designed to run on Linux systems. You can run it in Windows, but instructions are provided for Linux systems.

This tool was developed by Ash Nassef, Dr. Darren Pouliot, and Dr. Niloofar Alavi-Shoushtari to chip geolocated imagery (GeoTIFF, JPEG2000, etc.) and shapefiles for use with a deep learning algorithm. It effectively cuts up (or chips) large images and vectors into preset sizes than can be easily ingested by a deep learning algorithm. To run this tool, you will need the following:

1. Install [Anaconda](https://www.anaconda.com/download).
2. Clone this Git repository.
3. Set up the Chipper environment in Anaconda using the included ChipperEnv.yml specification file.
4. Activate the Chipper environment.
5. Edit the Chipper.py file. The locations of the imagery, mask shapefile, and index file are hardcoded and will allow dynamic input in a future iteration. For now, edit lines 33, 36, and 39 in Chipper.py to reflect the true location of your files.
6. Run the Chipper.py file using the following command from within the Chipper environment: python Chipper.py
