# for each .zip file in the current directory, extract the contents and save them in a new directory named after the .zip file

import os
import zipfile

# get the current directory
current_dir = os.getcwd()

# get the list of files in the current directory
files = os.listdir(current_dir)

# iterate over the files
for file in files:
    # check if the file is a .zip file
    if file.endswith('.zip'):
        try:
        # create a new directory with the same name as the .zip file
            directory_name = file.replace('.zip', '')
            os.makedirs(directory_name, exist_ok=True)
            
            # extract the contents of the .zip file to the new directory
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(directory_name)
                
            print(f'Extracted contents of {file} to {directory_name}')
        except Exception as e:
            print(f'Failed to extract contents of {file}: {e}')

# delete the .zip files
for file in files:
    if file.endswith('.zip'):
        os.remove(file)
        print(f'Deleted {file}')
