# Beachmeter
a simple tool for semi-automatic beach morphodynamics measurement

docs/Manual.pdf - a step-by-step guide on how to install and use the Beachmeter 1.2 inside the ArcGIS software 

src/Beachmeter.1.2.py - the source of code; a Python script using ArcPy package by ESRI

toolbox/Beachmeter.1.2.tbx - a ready-to-use ArcGIS (10.6 or higher) and ArcGIS Pro toolbox contains the Python script

Overview

Beachmeter is a Python script to automate the measurements of beaches based on a new delimitation method on digital elevation models (DEMs) of a coastal zone. It is developed to analyze multi-kilometre shorelines, especially in coastal monitoring. Filling out the Beachmeter form, the user inputs the raster DEMs from two measurement campaigns and information on the study site features. The Beachmeter delimits the beach boundaries and saves them as shapefiles. It creates beach elevation models, compares them to provide a differential map, and also measures the basic morphological parameters.

Keywords 

coastal monitoring, beach morphometry, shoreline changes, coastal management, ArcGIS tool, beach elevation model

License

Use Beachmeter 1.2 free. Develop it by modifying the source code to fit it to your work better. Add new features as you wish. If you achieve significant development of the Beachmeter, please send me your results so we can release a new version together. 

If you need help, send me an email: patryk.sitkiewicz@ug.edu.pl

The Beachmeter will be published as a scientific paper. Please cite it if you use it: 

Sitkiewicz P. (2024). Beachmeter – a simple tool for semi-automatic beach morphodynamics measurement.
