# Import the libraries you will use here.
import pandas as pd
import os
import pathlib
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

# Choose an excel file containing a list of orthophotos
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

# Save the path to the Excel file with the file names to a variable.
print('Opening file /mnt/datacube/Niloo/PythonCode/' + xlsx_list[choice -1] + ' and checking if files exist.')

# Use the pandas library to read the excel file and store it in a variable.
df_Filenames = pd.read_excel(excel_file)[['FileName']]

# Path to your orthophotos
path_orthophotos = '/mnt/LWFdata/'

# Keep track of the files with two lists.
missing = []
found = []
# Use a for loop to iterate through the columns.
for i in range(len(df_Filenames['FileName'])):
    # Use a flag variable (bool) to keep track of which files were found.
    file_found = False
    print('|--> Locating file: ' + df_Filenames['FileName'][i])
    
    # Use a nested for loop to iterate through the filenames in the orthophotos folder.
    for filename in os.listdir(path_orthophotos):
        # If the filename matches the one from the column, we'll use it.
        if filename == df_Filenames['FileName'][i] + ".tif":
            # Set file_found to True
            file_found = True
            # Break out of the nested for loop (do not continue iterating).
            break
    
    # Check if we found our file.
    if file_found == True:
        # Print which file was found.
        print('|---> Found file: ' + df_Filenames['FileName'][i])
        # Append the filename to the found list.
        found.append(df_Filenames['FileName'][i])
    
    # If we haven't found our file...
    else:
        # Print which file is missing, and append it to our missing_files text file.
        print("File '" + df_Filenames['FileName'][i] + "' not found.")
        # Append the missing file to the missing list.
        missing.append(df_Filenames['FileName'][i])

# Output the results to an excel spreadsheet with appropriate headers.
print("Found: " + str(len(found)) + ". Missing: " + str(len(missing)) + ".")
missing_output = pd.DataFrame({"Missing Files":missing})
found_output = pd.DataFrame({"Found Files":found})
path = pathlib.Path(__file__).parent.resolve()
if len(missing) > 0:
    missing_output.to_excel(str(path) + '/' + xlsx_list[choice -1] + '_Missing_Files.xlsx', sheet_name = 'sheet1', index = False)
if len(found) > 0:
    found_output.to_excel(str(path) + '/' + xlsx_list[choice -1] + '_Found_Files.xlsx', sheet_name = 'sheet1', index = False)
print("\n\nFinished!")
