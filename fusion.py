##REDD tools Costa Rica=group
##FusionClass=name
##RASTER_FILES_FOLDER=folder
##RESULTS_FOLDER=folder


import sys
import numpy as numpy
import glob
import os
import math
from osgeo import gdal, gdalconst, ogr

print(str(sys.argv))
print(sys.argv[1])
print(sys.argv[2])
# sys.exit()


# RASTER_FILES_FOLDER = "/home/mfvargas/Downloads/fusion_entrada/"
# RESULTS_FOLDER = "/home/mfvargas/Downloads/fusion_salida/"
RASTER_FILES_FOLDER = sys.argv[1]
RESULTS_FOLDER = sys.argv[2]

driver = gdal.GetDriverByName('GTiff')
driver.Register()

rasterFiles = glob.glob(os.path.join(RASTER_FILES_FOLDER, '*_*_*'))


# CREATE INPUT RASTER SOURCES LIST AND INPUT RASTER NAMES LIST
dataSourceRasterList = []
for i in range(len(rasterFiles)):
	dataSourceRasterList.append(gdal.Open(rasterFiles[i], 0))


# GET ROWS AND COLS LENGTH (MIN BETWEEN ALL INPUT RASTERS)
rows = dataSourceRasterList[0].RasterYSize
cols = dataSourceRasterList[0].RasterXSize
for i in range(0, len(dataSourceRasterList)):
	if dataSourceRasterList[i].RasterYSize < rows:
		rows = dataSourceRasterList[i].RasterYSize
	if dataSourceRasterList[i].RasterXSize < cols:
		cols = dataSourceRasterList[i].RasterXSize


# CREATE OUTPUT RASTER
outputRaster = driver.CreateCopy(os.path.join(RESULTS_FOLDER, 'outputRaster.tif'), dataSourceRasterList[0], 0)


# RASTERS BAND 1 LIST
band1List = []
for rasterIndex in range(len(dataSourceRasterList)):
	band1List.append(dataSourceRasterList[rasterIndex].GetRasterBand(1).ReadAsArray(0, 0, cols, rows))


# RASTERS BAND 2 LIST
band2List = []
for rasterIndex in range(len(dataSourceRasterList)):
	band2List.append(dataSourceRasterList[rasterIndex].GetRasterBand(2).ReadAsArray(0, 0, cols, rows))
  


# MAIN LOOP
percentage = 0
band1 = numpy.zeros((rows, cols), numpy.int8)
band1.fill(255)
band2 = numpy.zeros((rows, cols), numpy.int8)
band2.fill(255)
band3 = numpy.zeros((rows, cols), numpy.int8)
band3.fill(255)
for rowIndex in range(rows):  
	print("row: ", rowIndex)
	for colIndex in range(cols):		
		array = numpy.zeros(18, dtype=int)	
		array.fill(0)		
		# SUM(Percentage) BY CLASS
		for rasterIndex in range(len(rasterFiles)):
			classValue = band1List[rasterIndex][rowIndex, colIndex]
			percentageValue = band2List[rasterIndex][rowIndex, colIndex]
			if (classValue >= 0) & (classValue<=20) & (percentageValue>=0) & (percentageValue<=100):
				array[int(classValue)] += percentageValue
		# SELECTED CLASS BY MAX(Percentage) BY (SUM(Percentage) BY CLASS)
		selectedPercentage = 0
		selectedClass = -1
		for i in range(len(array)):
			if (array[i] > selectedPercentage):
				selectedPercentage = array[i]
				selectedClass = i
		#ADDED CONDITIO
		selectedPercentage = 0
		if (selectedClass == 9) & ( (array[11]!=0) | (array[16]!=0) | (array[17]!=0) ):
			selectedClass = 11
			selectedPercentage = array[11]
			if (array[16] > selectedPercentage):
				selectedClass = 16
				selectedPercentage = array[16]
			if (array[17] > selectedPercentage):
				selectedClass = 17
				selectedPercentage = array[17]
		# GET FINAL VALUES
		selectedPercentage = 0
		selectedRaster = -1
		if selectedClass != -1:			
			for rasterIndex in range(len(rasterFiles)):
				classValue = band1List[rasterIndex][rowIndex, colIndex]
				percentageValue = band2List[rasterIndex][rowIndex, colIndex]
				if (classValue == selectedClass) & (percentageValue > selectedPercentage) & (percentageValue != 255):
					selectedPercentage = percentageValue
					selectedRaster = rasterIndex	
			# FILL BANDS
			if selectedRaster != -1:			
				band1[rowIndex, colIndex] = band1List[selectedRaster][rowIndex, colIndex]
				band2[rowIndex, colIndex] = band2List[selectedRaster][rowIndex, colIndex]
				band3[rowIndex, colIndex] = selectedRaster
	if percentage != (100-((rows-rowIndex)*100)/rows):
		percentage = (100-((rows-rowIndex)*100)/rows)
	# progress.setPercentage(percentage)

outputRaster.GetRasterBand(1).WriteArray(band1)
outputRaster.GetRasterBand(2).WriteArray(band2)
outputRaster.GetRasterBand(3).WriteArray(band3)


# WRITE BAND 3 VALUES ON TEXT FILE 
txtfile = open(os.path.join(RESULTS_FOLDER, 'outputInfo.txt'), 'w')
for i in range(len(rasterFiles)):
	aux = str(i) + ": " + rasterFiles[i] + "\n"
	txtfile.write("{0}".format(aux))
txtfile.close( )
