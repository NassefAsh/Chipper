from functions import *
import shutil
import pandas as pd
import string
from time import sleep

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(bcolors.HEADER + '\nImage Chipping Tool version 4, 07 NOV 2022' + bcolors.ENDC)
print(bcolors.BOLD + 'For support, contact Ash Nassef (nassef.ash@gmail.com)\n' + bcolors.ENDC)
print(bcolors.BOLD + 'This tool is designed to create image chips for deep learning.' + bcolors.ENDC)
print(bcolors.BOLD + 'Inputs: ' + bcolors.ENDC)
print(bcolors.WARNING + '         Orthophotos (GeoTIFF format - .tif)' + bcolors.ENDC)
print(bcolors.WARNING + '         Mask file covering the AOI represented by the Orthophotos (shapefile - .shp + accompanying files)' + bcolors.ENDC)
print(bcolors.WARNING + '         List of orthophoto filenames to be used (spreadsheet - .xlsx)' + bcolors.ENDC) 
print(bcolors.BOLD + '\n\nOutputs: ' + bcolors.ENDC)
print(bcolors.WARNING + '         Chipped orthophotos (GeoTIFF format - .tif)' + bcolors.ENDC)
print(bcolors.WARNING + '         Chipped masks (shapefile - .shp + accompanying files)' + bcolors.ENDC)
print(bcolors.WARNING + '         Footprints of each input Orthophoto (shapefile - .shp)\n\n\n' + bcolors.ENDC)

# Paths
#Path of your orthophotos. The actual network path needs to be mounted to a folder. Ask Ash to mount it for you and set it here.
path_orthophotos_input = '/mnt/LWFdata/' 

#Path to the mask shapefile. This mask should have polygons with a CID column, where values are integers representing the different features.
mask = ogr.Open('/mnt/datacube/Niloo/PythonCode/LWFAllSamples/LWFAllSamplesONFinal.shp') 

#Path to the index shapefile. 
index = ogr.Open('/mnt/datacube/Niloo/PythonCode/LWFAllSamples/DRAPE_2019Index.shp')

#Path to the excel spreadsheet with a list of orthophoto filenames to be processed. 
#The header (column name) should be "FileName" and the filenames should not have an extension. (i.e. filename1, not filename1.tif)
xlsx_list = []
num = 1
for file in os.listdir('/mnt/datacube/Niloo/PythonCode/LWFLists'):
    if file[-5:] == '.xlsx':
        xlsx_list.append(file)
        print(bcolors.OKCYAN + str(num) + ':', file + bcolors.ENDC)
        num += 1

choice = int(input('\nChoose from the available files: '))
excel_file = '/mnt/datacube/Niloo/PythonCode/LWFLists/' + xlsx_list[choice - 1]
print(bcolors.WARNING + '\n --->>  ' + xlsx_list[choice - 1], 'selected.  <<---' + bcolors.ENDC)
sleep(0.25)

#Path to where you want the output of this script (chips) to be saved.
path_output = '/mnt/datacube/Niloo/PythonCode/DRAPE2019Ortho_Output/' + xlsx_list[choice - 1][:-5]
print(bcolors.WARNING + '\nOutput path: ' + path_output + '\n' + bcolors.ENDC)
path_output = str(input('\nEnter the (case sensitive) output path where chips will be saved' + bcolors.OKGREEN + ' /mnt/datacube/Niloo/PythonCode/DRAPE2019Ortho_Output/: ' + bcolors.ENDC) or '/mnt/datacube/Niloo/PythonCode/DRAPE2019Ortho_Output/')
sleep(0.25)
verbose = str(input('\nWould you like verbose output?' + bcolors.OKGREEN + ' [Y/n]: ' + bcolors.ENDC) or 'y').lower()
# Use the pandas library to read the excel file and store it in a variable.
# Note that we are specifying the column named 'FileName' and ignoring the other columns.
# Only this column will be store in our variable.
# This variable holds our DataFrame (the contents of the Excel file in this case).
df_Filenames = pd.read_excel(excel_file)[['FileName']]

numFiles = len(df_Filenames['FileName'])
print(bcolors.FAIL + "\n\nPress CTRL-C at any time to cancel and quit.\n\n" + bcolors.ENDC)
sleep(0.25)
print(bcolors.HEADER + "Note: If partially processed images exist in the", path_output,"folder, they will be skipped. Delete existing numbered folders to reprocess.\n" + bcolors.ENDC)
print("There are " + str(numFiles + 1) + " .tif files in", path_orthophotos_input)
print("You can choose how many images you would like to process, and at which index to start (from 0 to " + str(numFiles) + ", inclusively, for a total of " + str(numFiles+1) + ")\n\n")
# Get sample size to process and start index
sampleSize = int(input('How many images would you like to process? ' + bcolors.OKGREEN + '[' + str(len(df_Filenames['FileName'])) + ']: ' + bcolors.ENDC) or numFiles)
startIndex = int(input('At which index would you like to start? ' + bcolors.OKGREEN + '[0]: ' + bcolors.ENDC) or 0)
# Check for user error and handle it
if numFiles - sampleSize < startIndex:
    print("You have entered index " + str(startIndex) + " and asked for " + str(sampleSize) + " images to be processed.")
    cont = str(input("Starting at index " + bcolors.WARNING + str(startIndex) + bcolors.ENDC + ", there are only " + bcolors.WARNING + str(numFiles - startIndex) + bcolors.ENDC + " images to process. Would you like to continue" + bcolors.OKGREEN + " [Y/n]? " + bcolors.ENDC) or 'y').lower()
    # If the answer is anything by yes or no, keep asking.
    while cont != 'y' and cont != 'Y' and cont != 'n' and cont != 'N':
        cont = str(input("Sorry, your answer was unclear. Would you like to continue" + bcolors.OKGREEN + " [Y/n]? " + bcolors.ENDC) or 'y').lower()
    # If the answer is no, quit.
    if cont == 'n' or cont == 'N':
        print(bcolors.BOLD + bcolors.OKBLUE + "Goodbye." + bcolors.ENDC)
        sys.exit()

# Get chip size
xSize = int(input('Enter chip X size ' + bcolors.OKGREEN + '[625]: ' + bcolors.ENDC) or 625)
ySize = int(input('Enter chip Y size ' + bcolors.OKGREEN + '[625]: ' + bcolors.ENDC) or 625)

StartTime = datetime.now()
print('\nStart Time: ', StartTime.strftime('%H:%M:%S.%f')[:-3] + '\n\n')

fieldName = str(input('Which field represents the feature values?' + bcolors.OKGREEN + ' [CID]: ' + bcolors.ENDC) or 'CID')
fileExtension = str(input('What is your file extension? Use the following formate: .abc including the dot.' + bcolors.OKGREEN + ' [.tif]: ' + bcolors.ENDC) or '.tif')
# Start processing the images.
for i in range(len(df_Filenames['FileName'])):
    filename = df_Filenames['FileName'][i]
    # If the image we're on preceeds our starting image index, increment and retry
    if i < startIndex:
        continue
    # Keep track of processing time.
    ProcessingStartTime = datetime.now()
    print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Opening file: ' + filename)

# 1. Open the orthophoto.
    try:
        file = gdal.Open(path_orthophotos_input + filename + fileExtension)
    except:
        print("Cannot find " + path_orthophotos_input + filename + fileExtension + ". Continuing to next image.")
        continue
    if verbose == 'y': 
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
    print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Creating footprint polygon...')
    
# 2. Extract the index for this file to use as a footprint polygon.
    # Export a selected feature from the index matching the filename.
    layer = index.GetLayer(0)
    footprint = None
    adjustedFilename = filename[:-6] + '9DRAPE'
    fieldIndex = layer[0].GetFieldIndex('FileName') #index of the FileName field
    print('adjustedFilename = ' + adjustedFilename)
    for feat in layer:
        if feat.GetFieldAsString(fieldIndex).lower() == adjustedFilename.lower():
            footprint = feat
            layer.ResetReading()
            break
            
    geom = footprint.GetGeometryRef()
    
    # Reproject the geometry before proceeding further.
    geom.Transform(osr.CoordinateTransformation(layer.GetSpatialRef(),file.GetSpatialRef()))
    
    polygon = shapely.wkb.loads(geom.ExportToIsoWkb())
    
    if verbose == 'y':
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
    
# 3. Save the footprint polygon to a shapefile.
    SavePolygonToShapefile(path_output, filename, polygon, GetSRS(file), 'Footprint_' + str(i))
    
# 4. Open the footprint polygon.
    exportedPolygon = ogr.Open(path_output + '/' + filename + '/Footprint_' + str(i) + '.shp')
    
# 5. Create a mask shapefile and add a layer to it.
    clippedPolygonDS = CreateDataSource(path_output + '/' + filename + '/Mask_' + str(i) + '.shp')
    outputLayer = CreateLayer(clippedPolygonDS, 'Mask_' + str(i), GetSRS(file), ogr.wkbMultiPolygon)
    print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Clipping polygon...')
    
# 6. a) Clip the mask polygon layer using the footprint polygon, and output it to the mask layer.
    ClipPolygon(mask, exportedPolygon, outputLayer)
    
#    b) Check if the clipped mask contains relevant values.
    relevant = False
    
    print('Number of features found:', outputLayer.GetFeatureCount())
   
    for feature in outputLayer:
        if relevant == True:
            break
        if feature.GetField(fieldName) > 0:
            if verbose == 'y': 
                print('Relevant features found. Continuing process.')
            relevant = True
            
    if relevant == False:
        if verbose == 'y':
            print('This chip does not contain relevant data. Skipping...')
        # Clean up the files if any have been created so far.
        if not os.path.isdir(path_output + '/' + filename):
            continue
        
        file = footprint = feat = geom = polygon = exportedPolygon = outputLayer = clippedPolygonDS = None
        os.system('rm -R ' + path_output + '/' + filename)
        continue
    else:
        if verbose == 'y':
            print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Rasterizing...')
        
# 7. Rasterize the clipped polygon and save it to file.
    Rasterize(clippedPolygonDS, fieldName, path_output + '/' + filename + '/' + 'Raster' + str(i) + '.tif', file)
    if verbose == 'y':
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
    
# 8. If the mask_chips folder doesn't exist, create it.
    if not os.path.isdir(path_output + '/' + filename + '/mask_chips'):
        os.mkdir(path_output + '/' + filename + '/mask_chips')
        
# 9. If the ortho_chips folder doesn't exist, create it.
    if not os.path.isdir(path_output + '/' + filename + '/ortho_chips'):
        os.mkdir(path_output + '/' + filename + '/ortho_chips')
    print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Chipping mask...')
    
# 10. Open the mask (rasterized clipped polygon from step 7).
    raster = gdal.Open(path_output + '/' + filename + '/' + 'Raster' + str(i) + '.tif')
    
# 11. Set the projection to match the orthophoto.
    raster.SetProjection(file.GetProjection())
    
# 12. Chip the mask.
    ChipImage(raster, path_output + '/' + filename + '/mask_chips/mask' + str(i) + '-', xSize, ySize, verbose)
    if verbose == 'y':
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
    print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - Chipping orthophoto...')
    
# 13. Chip the orthophoto.
    ChipImage(file, path_output + '/' + filename + '/ortho_chips/ortho' + str(i) + '-', xSize, ySize, verbose)
    if verbose == 'y':
        print(str(datetime.now().strftime('%H:%M:%S.%f')[:-3]) + ' - ... done.')
        print('Total Processing Time: ' + GetElapsedTime(ProcessingStartTime, datetime.now()))
    
# 14. Free up memory/close files.
    file = projection = extent = polygon = exportedPolygon = outputLayer = ProcessingStartTime = clippedPolygonDS = None

EndTime = datetime.now()
print('End Time: ', EndTime.strftime('%H:%M:%S.%f')[:-3])
print('Total Time: ', GetElapsedTime(StartTime, EndTime))