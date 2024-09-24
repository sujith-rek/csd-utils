import os
import re
import subprocess
import shutil

OUTPUT_DIR = os.path.abspath('output')
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

RUN_DIR = os.path.abspath('run')
if not os.path.exists(RUN_DIR):
    os.makedirs(RUN_DIR)

folder_re = re.compile(r'Link to submit Lab Exam \(P2\)_([a-z0-9]+)_attempt_.*')

# # for each directory, check if Main.java or main.java exists
# # then create a copy of that file in the run directory with the public class name as the filename and compile, run it, send the output to a file with id extracted from the directory name

for dirname in os.listdir('.'):
    if os.path.isdir(dirname):
        match = folder_re.match(dirname)
        if match:
            id = match.group(1)
            main_file = None
            main_file_path = None
            main_file_dir = None
            
            for root, _, files in os.walk(dirname):
                if 'Main.java' in files:
                    main_file = 'Main.java'
                    main_file_path = os.path.join(root, main_file)
                    main_file_dir = root
                    break
                elif 'main.java' in files:
                    main_file = 'main.java'
                    main_file_path = os.path.join(root, main_file)
                    main_file_dir = root
                    break
            
            if main_file:
                try:
                    # Read the first few lines to check for a package statement
                    package_dir = ''
                    package_name = ''
                    with open(main_file_path, 'r') as f:
                        for line in f:
                            if line.strip().startswith('package'):
                                package_name = line.strip().split()[1].rstrip(';')
                                package_dir = package_name.replace('.', '/')
                                break
                    
                    # Create a new folder inside RUN_DIR with the name extracted from the regex
                    run_subdir = os.path.join(RUN_DIR, id)
                    if not os.path.exists(run_subdir):
                        os.makedirs(run_subdir)
                    
                    # If package_dir is not empty, create the directory structure
                    if package_dir:
                        run_subdir = os.path.join(run_subdir, package_dir)
                        if not os.path.exists(run_subdir):
                            os.makedirs(run_subdir)
                    
                    # Copy the entire directory containing main_file to the new folder inside RUN_DIR
                    if main_file_dir:
                        for item in os.listdir(main_file_dir):
                            s = os.path.join(main_file_dir, item)
                            d = os.path.join(run_subdir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)
                    
                    # Change directory to the root of the package structure
                    original_dir = os.getcwd()
                    os.chdir(run_subdir)
                    os.chdir('../')
                    
                    # Compile the Java file
                    compile_process = subprocess.run(['javac', os.path.join(run_subdir, main_file)], capture_output=True, text=True)
                    if compile_process.returncode != 0:
                        raise Exception(f"Compilation failed: {compile_process.stderr}")
                
                    # Run the compiled Java class
                    class_name = main_file.split('.')[0]
                    if package_name:
                        class_name = f"{package_name}.{class_name}"
                    run_process = subprocess.run(['java', class_name], capture_output=True, text=True)
                    
                    # Determine the output based on the return code
                    if run_process.returncode == 0:
                        output = run_process.stdout
                    else:
                        output = run_process.stderr
                
                    # Write the output to the file
                    with open(os.path.join(OUTPUT_DIR, id + '.txt'), 'w') as f:
                        f.write(output)
                
                except Exception as e:
                    error_message = f'Error while running {dirname}: {e}'
                    with open(os.path.join(OUTPUT_DIR, id + '_error.txt'), 'w') as f:
                        f.write(error_message)
                finally:
                    # Change back to the original directory
                    os.chdir(original_dir)
            else:
                with open(os.path.join(OUTPUT_DIR, id + '_error.txt'), 'w') as f:
                    f.write('no main found')

# print('Done')

for dirname in os.listdir("."):
    if os.path.isdir(dirname):
        match = folder_re.match(dirname)
        # create a new dir in the root of the project with the id
        # if a dir with the id exists in "RUN_DIR", move it here
        # if <id>.txt or <id>_error.txt exists in "OUTPUT_DIR", move it here
        if match:
            id = match.group(1)
            new_dir = os.path.join(os.getcwd(), id)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            
            old_dir = os.path.join(RUN_DIR, id)
            if os.path.exists(old_dir):
                shutil.move(old_dir, new_dir)
            else:
                print(f"Directory {old_dir} does not exist")
                shutil.move(dirname, new_dir)
            
            
            output_file = os.path.join(OUTPUT_DIR, id + '.txt')
            
            if os.path.exists(output_file):
                shutil.move(output_file, new_dir)
        
            error_file = os.path.join(OUTPUT_DIR, id + '_error.txt')
            if os.path.exists(error_file):
                shutil.move(error_file, new_dir)
            
            shutil.rmtree(dirname)
        
print('Done')
            
        