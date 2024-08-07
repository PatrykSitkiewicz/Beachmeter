#--------------------------------
# Name:        Beachmeter 1.21
# Author:   Patryk Sitkiewicz
# Created     02 December 2023
# Last update: 07 August 2024
# Cite it as:   Sitkiewicz P. (2024). Beachmeter - a simple tool for semi-automatic beach morphodynamics measurement. SoftwareX
# tested in ArcGIS Pro Version:   3.2
# Python Version:   3.9.18
# This script version is meant to be used in the ArcGIS by ESRI.
#--------------------------------


# ----- Setup -----

# import
import os
import sys
import arcpy, datetime
from sys import argv

# Check out the licenses
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("spatial")

# Overwrite existing data
arcpy.env.overwriteOutput = True

# ----- Inputs and outputs -----

# Set local settings for the specific study area
shore_name = arcpy.GetParameterAsText(0).replace(" ","")
seaward_limit = arcpy.GetParameterAsText(1)
landward_limit = arcpy.GetParameterAsText(2)

# Input coast digital elevation models (reference and after changes)
DEM_before = arcpy.GetParameterAsText(3)
timestamp_before = arcpy.GetParameterAsText(4)
DEM_after = arcpy.GetParameterAsText(5)
timestamp_after = arcpy.GetParameterAsText(6)

# Set spatial dimensions parameters
expected_area = arcpy.GetParameterAsText(7)
expected_length = arcpy.GetParameterAsText(8)

# Automatic ArcGIS workspace (geodatabase) creation and set
if not arcpy.Exists(r"C:/Beachmeter"):
    arcpy.CreateFolder_management(r"C:/", "Beachmeter")
   
today = str(datetime.date.today())
today_newfolder = arcpy.CreateFolder_management(r"C:/Beachmeter/", today)
GDB_location = arcpy.management.CreateFileGDB(today_newfolder, shore_name + ".gdb")
arcpy.env.workspace = str(GDB_location)


# -------------------------------- 
# ----- Draw seaward and landward limits of the beach -----
# --------------------------------

# ----- Draw beach boundaries BEFORE changes -----

# ----- SEAWARD LIMIT -----
# Process: draw seaward contour (Contour) (3d)
before_seaward_lines = arcpy.env.workspace + "\\before_seaward_lines"
arcpy.ddd.Contour(in_raster=DEM_before, out_polyline_features=before_seaward_lines, contour_interval=10000, base_contour=seaward_limit)

# Process: Select too short (1) (Select Layer By Attribute) (management)
too_short_contours_1_, Count_1_ = arcpy.management.SelectLayerByAttribute(in_layer_or_view=before_seaward_lines, where_clause="Shape_Length < " + expected_length)

# Process: Delete too short (1) (Delete Features) (management)
Output_waterline_1 = arcpy.management.DeleteFeatures(in_features=too_short_contours_1_)[0]

# Process: Smooth seaward contour (1) (Smooth Line) (cartography)
before_waterline = arcpy.env.workspace + "\\" + shore_name + timestamp_before +"_sea_line"
with arcpy.EnvManager(transferGDBAttributeProperties=False):
    arcpy.cartography.SmoothLine(in_features=Output_waterline_1, out_feature_class=before_waterline, algorithm="PAEK", tolerance="2 Meters", error_option="RESOLVE_ERRORS")

# ----- LANDWARD LIMIT -----
# Process: draw landward contour (Contour) (3d)
before_landward_contours = arcpy.env.workspace + "\\before_landward_lines"
arcpy.ddd.Contour(in_raster=DEM_before, out_polyline_features=before_landward_contours, contour_interval=10000, base_contour=landward_limit)

# Process: Select too short (2) (Select Layer By Attribute) (management)
too_short_contours_2_, Count_2_ = arcpy.management.SelectLayerByAttribute(in_layer_or_view=before_landward_contours, where_clause="Shape_Length < " + expected_length)

# Process: Delete too short (2) (Delete Features) (management)
Output_beach_landward_limit_2 = arcpy.management.DeleteFeatures(in_features=too_short_contours_2_)[0]

# Process: Smooth landward contour (2) (Smooth Line) (cartography)
before_landward = arcpy.env.workspace + "\\" + shore_name + timestamp_before +"_land_line"
with arcpy.EnvManager(transferGDBAttributeProperties=False):
    arcpy.cartography.SmoothLine(in_features=Output_beach_landward_limit_2, out_feature_class=before_landward, algorithm="PAEK", tolerance="10 Meters", error_option="RESOLVE_ERRORS")

# ----- SHORE BASELINE -----
# Process: Smooth landward contour more to obtain a generalized shoreline (3) (Smooth Line) (cartography)
shore_baseline = arcpy.env.workspace + "\\" + shore_name + "_baseline" 
with arcpy.EnvManager(transferGDBAttributeProperties=False):
    arcpy.cartography.SmoothLine(in_features=Output_beach_landward_limit_2, out_feature_class=shore_baseline, algorithm="PAEK", tolerance="500 Meters", error_option="RESOLVE_ERRORS")

# Measure and print the length of the generalized shoreline
with arcpy.da.SearchCursor(shore_baseline, "SHAPE@LENGTH") as cursor:
    for row in cursor:
        shoreline_length = round(float(u'{0}'.format(row[0])), None)
arcpy.AddMessage("The approximate length of the analyzed shore section is " + str(shoreline_length) + " meters.")


# ----- Draw beach boundaries AFTER changes -----

# ----- SEAWARD LIMIT -----
# Process: draw seaward contour (Contour) (3d)
after_seaward_lines = arcpy.env.workspace + "\\after_seaward_lines"
arcpy.ddd.Contour(in_raster=DEM_after, out_polyline_features=after_seaward_lines, contour_interval=10000, base_contour=seaward_limit)

# Process: Select too short (3) (Select Layer By Attribute) (management)
too_short_contours_3_, Count_3_ = arcpy.management.SelectLayerByAttribute(in_layer_or_view=after_seaward_lines, where_clause="Shape_Length < " + expected_length)

# Process: Delete (3) (Delete Features) (management)
Output_waterline_3 = arcpy.management.DeleteFeatures(in_features=too_short_contours_3_)[0]

# Process: Smooth seaward contour (3) (Smooth Line) (cartography)
after_waterline = arcpy.env.workspace + "\\" + shore_name + timestamp_after +"_sea_line"
with arcpy.EnvManager(transferGDBAttributeProperties=False):
    arcpy.cartography.SmoothLine(in_features=Output_waterline_3, out_feature_class=after_waterline, algorithm="PAEK", tolerance="2 Meters", error_option="RESOLVE_ERRORS")

# ----- LANDWARD LIMIT -----
# Process: draw landward contour (Contour) (3d)
after_landward_contours = arcpy.env.workspace + "\\after_landward_lines"
arcpy.ddd.Contour(in_raster=DEM_after, out_polyline_features=after_landward_contours, contour_interval=10000, base_contour=landward_limit)

# Process: Select too short (4) (Select Layer By Attribute) (management)
too_short_contours_4_, Count_4_ = arcpy.management.SelectLayerByAttribute(in_layer_or_view=after_landward_contours, where_clause="Shape_Length < " + expected_length)

# Process: Delete too short (4) (Delete Features) (management)
Output_beach_landward_limit_4 = arcpy.management.DeleteFeatures(in_features=too_short_contours_4_)[0]

# Process: Smooth landward contour (4) (Smooth Line) (cartography)
after_landward = arcpy.env.workspace + "\\" + shore_name + timestamp_after +"_land_line"
with arcpy.EnvManager(transferGDBAttributeProperties=False):
    arcpy.cartography.SmoothLine(in_features=Output_beach_landward_limit_4, out_feature_class=after_landward, algorithm="PAEK", tolerance="10 Meters", error_option="RESOLVE_ERRORS")


# -------------------------------- 
# ----- Clip the beach area from DEM -----
# --------------------------------


# ----- Clip the beach before changes (point of reference) -----
# Process: before polygon (Contour) (3d)
before_polygons = arcpy.env.workspace + "\\before_polygons"
interval_1 = (float(landward_limit.replace(",",".")) - float(seaward_limit.replace(",",".")))
arcpy.ddd.Contour(in_raster=DEM_before, out_polyline_features=before_polygons, contour_interval=interval_1, base_contour=seaward_limit, contour_type="CONTOUR_POLYGON")

# Process: Select before small polygons (Select Layer By Attribute) (management)
Contour_1 = landward_limit.replace(",",".")
before_polygon_Layer, Count = arcpy.management.SelectLayerByAttribute(in_layer_or_view=before_polygons, where_clause="ContourMax <> " + Contour_1)

# Process: Delete before small polygons (Delete Features) (management)
Output_before_polygon = arcpy.management.DeleteFeatures(in_features=before_polygon_Layer)[0]

# Process: Eliminate before Polygon Part (Eliminate Polygon Part) (management)
before_polygon = arcpy.env.workspace + "\\before_polygon"
arcpy.management.EliminatePolygonPart(in_features=Output_before_polygon, out_feature_class=before_polygon, condition="AREA", part_area=expected_area+" SquareMeters", part_area_percent=1, part_option="ANY")

# Process: Clip before Raster (Clip Raster) (management)
Beach_Before_DEM = arcpy.env.workspace + "\\" + shore_name + timestamp_before +"_DEM"
desc_before = arcpy.Describe(before_polygon)
rectangle_before = str(desc_before.extent)
arcpy.management.Clip(in_raster=DEM_before, rectangle=rectangle_before, out_raster=Beach_Before_DEM, in_template_dataset=before_polygon, clipping_geometry="ClippingGeometry")
Beach_Before_DEM = arcpy.Raster(Beach_Before_DEM)


# ----- Clip beach after changes -----
# Process: after polygon (Contour) (3d)
after_polygons = arcpy.env.workspace + "\\after_polygons"
arcpy.ddd.Contour(in_raster=DEM_after, out_polyline_features=after_polygons, contour_interval=interval_1, base_contour=seaward_limit, contour_type="CONTOUR_POLYGON")

# Process: Select before small polygons (Select Layer By Attribute) (management)
after_polygon_Layer, Count = arcpy.management.SelectLayerByAttribute(in_layer_or_view=after_polygons, where_clause="ContourMax <> " +  Contour_1)

# Process: Delete before small polygons (Delete Features) (management)
Output_after_polygon = arcpy.management.DeleteFeatures(in_features=after_polygon_Layer)[0]

# Process: Eliminate before Polygon Part (Eliminate Polygon Part) (management)
after_polygon = arcpy.env.workspace + "\\after_polygon"
arcpy.management.EliminatePolygonPart(in_features=Output_after_polygon, out_feature_class=after_polygon, condition="AREA", part_area=expected_area+" SquareMeters", part_area_percent=1, part_option="ANY")
      
# Process: Clip after Raster (Clip Raster) (management)
Beach_After_DEM = arcpy.env.workspace + "\\" + shore_name + timestamp_after + "_DEM"
desc_after = arcpy.Describe(after_polygon)
rectangle_after = str(desc_after.extent)
arcpy.management.Clip(in_raster=DEM_after, rectangle=rectangle_after, out_raster=Beach_After_DEM, in_template_dataset=after_polygon, clipping_geometry="ClippingGeometry")
Beach_After_DEM = arcpy.Raster(Beach_After_DEM)


# -------------------------------- 
# ----- Beach Measurment -----
# --------------------------------

# Measure the beach area BEFORE
with arcpy.da.SearchCursor(before_polygon, "SHAPE@AREA") as cursor:
    for row in cursor:
        area_before = round(float(u'{0}'.format(row[0])), None)

# Measure beach average width BEFORE
width_before = round(area_before / shoreline_length, None)

# Measure beach area AFTER
with arcpy.da.SearchCursor(after_polygon, "SHAPE@AREA") as cursor:
    for row in cursor:
        area_after = round(float(u'{0}'.format(row[0])), None)

# Measure beach average width AFTER
width_after = round(area_after / shoreline_length, None)

# Print beach morphometry
arcpy.AddMessage(timestamp_before + " -> the " + shore_name + " beach area was " + str(area_before) + " square meters")
arcpy.AddMessage(timestamp_after + " -> the " + shore_name + " beach area was " + str(area_after) + " square meters")
arcpy.AddMessage(timestamp_before + " -> the " + shore_name + " beach average width was " + str(width_before) + " meters")
arcpy.AddMessage(timestamp_after + " -> the " + shore_name + " beach average width was " + str(width_after) + " meters")

# ----- Beach Sediments Volume above the seaward limit elevation -----
# Volume before
Beach_Before_Volume = str(today_newfolder) + "\\" + shore_name + timestamp_before + "_volume.csv"
arcpy.ddd.SurfaceVolume(in_surface=Beach_Before_DEM, out_text_file=Beach_Before_Volume, base_z=seaward_limit)

# Volume after
Beach_After_Volume = str(today_newfolder) + "\\" + shore_name + timestamp_after + "_volume.csv"
arcpy.ddd.SurfaceVolume(in_surface=Beach_After_DEM, out_text_file=Beach_After_Volume, base_z=seaward_limit)

# ----- Inform about the results  -----
arcpy.AddMessage("The beach surface area and its sediment volume above the seaward elevation limit have been saved: " +
                 Beach_Before_Volume + " and " +
                 Beach_After_Volume)

arcpy.AddMessage("You can find digital elevation models of your beach in the current working folder: " + arcpy.env.workspace)

# -------------------------------- 
# ----- Compare beach DEMs and generate differential map -----
# --------------------------------

# ----- Create a big beach polygon representing the area occupied by the beach before and the beach after  -----
big_polygon = arcpy.env.workspace + "\\big_polygon"
arcpy.management.Merge(
    inputs="before_polygon;after_polygon",
    output=big_polygon
)

# ----- 'After DEM' minus 'Before DEM'  -----
minusDEM = arcpy.env.workspace + "\\" + shore_name + "_DEM_minus"
arcpy.ddd.Minus(
    in_raster_or_constant1=DEM_after,
    in_raster_or_constant2=DEM_before,
    out_raster=minusDEM
)

# ----- Clip differential map to the beach area  -----
differDEM = arcpy.env.workspace + "\\" + shore_name + "_DEM_difference"
desc_differ = arcpy.Describe(big_polygon)
rectangle_differ = str(desc_differ.extent)
arcpy.management.Clip(in_raster=minusDEM, rectangle=rectangle_differ, out_raster=differDEM, in_template_dataset=big_polygon, clipping_geometry="ClippingGeometry")
differDEM = arcpy.Raster(differDEM)

# ----- Inform about the results  -----
if arcpy.Exists(minusDEM):
    arcpy.AddMessage("The " + shore_name + " beach differential map has been generated with success: " + str(differDEM))
else:
    arcpy.AddError("Raster math, Beach_After_DEM minus Beach_Before_DEM has been failed")

# calculate volume net loss
net_loss = str(today_newfolder) + "\\" + shore_name + timestamp_after + "_vol_loss.txt"
arcpy.ddd.SurfaceVolume(
    in_surface=differDEM,
    out_text_file= net_loss,
    reference_plane="BELOW",
    base_z=0,
    z_factor=1,
    pyramid_level_resolution=0
)

# calculate volume net gain
net_gain = str(today_newfolder) + "\\" + shore_name + timestamp_after + "_vol_gain.txt"
arcpy.ddd.SurfaceVolume(
    in_surface=differDEM,
    out_text_file= net_gain,
    reference_plane="ABOVE",
    base_z=0,
    z_factor=1,
    pyramid_level_resolution=0
)

# ----- Inform about the results  -----
arcpy.AddMessage("The " + shore_name + " beach volume loss and gain were calculated and saved: " + str(net_loss) + " and " + str(net_gain))


# ----- Clean -----
# Delete temporary files
arcpy.management.Delete(r"'before_polygons'; 'before_polygon'; 'big_polygon'; 'after_polygons'; 'after_polygon'; 'before_seaward_lines'; 'before_landward_lines'; 'after_seaward_lines'; 'after_landward_lines'", "")
arcpy.management.Delete(str(shore_name + "_DEM_minus"))
