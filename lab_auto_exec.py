import os
import re
import subprocess


OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

RUN_DIR = 'run'
if not os.path.exists(RUN_DIR):
    os.makedirs(RUN_DIR)

file_re = re.compile(r'Link to submit Lab Exam \(P1\)_([a-z0-9]+)_attempt_.*\.java')
public_class_re = re.compile(r'public class\s+([^\s{]+)\s*{?')

# for each file that ends with .java, read the file and extract the public class name
# then create a copy of that file in the run directory with the public class name as the filename and compile, run it, send the output to a file with id extracted from the filename

for filename in os.listdir('.'):
    if filename.endswith('.java'):
        match = file_re.match(filename)
        class_name = None
        if match:
            id = match.group(1)
            with open(filename, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    match = public_class_re.match(line)
                    if match:
                        class_name = match.group(1)
                        break
            try:
                # Remove lines with packages
                lines = [line for line in lines if not line.strip().startswith('package')]
            
                # Write the modified content to the Java file
                java_file_path = os.path.join(RUN_DIR, class_name + '.java')
                with open(java_file_path, 'w') as f:
                    f.write(''.join(lines))
                
                # Compile the Java file
                compile_process = subprocess.run(['javac', java_file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    raise Exception(f"Compilation failed: {compile_process.stderr}")
            
                # Run the compiled Java class
                run_process = subprocess.run(['java', '-cp', RUN_DIR, class_name], capture_output=True, text=True)
                
                # Determine the output based on the return code
                if run_process.returncode == 0:
                    output = run_process.stdout
                else:
                    output = run_process.stderr
            
                # Write the output to the file
                with open(os.path.join(OUTPUT_DIR, id + '.txt'), 'w') as f:
                    f.write(output)
                
                print(f'Output for {filename} written to {id}.txt')
                print(output)
            
            except Exception as e:
                error_message = f'Error while running {filename}: {e}'
                print(error_message)
                with open(os.path.join(OUTPUT_DIR, id + '_error.txt'), 'w') as f:
                    f.write(error_message)

print('Done')


for filename in os.listdir('.'):
    if filename.endswith('.java'):
        match = file_re.match(filename)
        if match:
            id = match.group(1)
            # create a folder in the current directory with the id
            # read the <id>.txt from OUTPUT_DIR and write it to the file in the folder
            # move the java file to the folder
            folder_path = os.path.join(os.getcwd(), id)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            os.rename(filename, os.path.join(folder_path, filename))
            try:
                with open(os.path.join(OUTPUT_DIR, id + '.txt'), 'r') as f:
                    with open(os.path.join(folder_path, id + '.txt'), 'w') as f2:
                        f2.write(f.read())
            except FileNotFoundError:
                try:
                    with open(os.path.join(OUTPUT_DIR, id + '_error.txt'), 'r') as f:
                        with open(os.path.join(folder_path, id + '_error.txt'), 'w') as f2:
                            f2.write(f.read())
                except FileNotFoundError:
                    print(f'No output found for {filename}')
            print(f'{filename} moved to {folder_path}')
print('Done')
