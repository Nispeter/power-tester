from flask import Flask, request, render_template, abort, url_for, redirect, make_response, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import random
import socket
import json
import zipfile
import threading as th
import time
from statistics import mean
import sys
import numpy as np
from dataProcessing import *
from socketUtils import *
import os
#import os

# Initialize the Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Create an empty list to store measurement queue items
queuelist = []
# statusdict = OrderedDict()
# Define routes and their respective functions

@app.route('/hola', methods=['GET'])
def hola():
    t = subprocess.run(['ls', 'status'], capture_output=True, universal_newlines=True)
    return str(t.stdout)

@app.route('/<code>/mean')
def jsonifyMean(code):
    df = pd.DataFrame()
    dicc = {}
    try:
        df = pd.read_csv('static/'+code+'/'+code+'ResultsFinal.csv')
    except FileNotFoundError:
        abort(404)

    for columni in range(20):
        test = df.iloc[:, columni]
        try:
         tmp = f'{round(mean(test), 3):,}'
         tmp = tmp.replace('.', ':')
         tmp = tmp.replace(',', '.')
         tmp = tmp.replace(':', ',')
        except TypeError:
         tmp = '<No medido>'
        dicc[test.name] = tmp
    return jsonify(dicc), 200


@app.route('/test', methods=['GET'])
def test():
    return render_template("index.html")

@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('test'))

# Route to check the status of a code execution
@app.route('/checkstatus/<code>', methods=['GET'])
def tmr(code):
    try:
        temp = open("status/"+code, 'r+', newline='\n')
    except FileNotFoundError:
        abort(404)
    data = temp.read()
    response = make_response(data, 200)
    response.headers["content-type"] = "text/plain;charset=UTF-8"
    return response

# Route to check the status of measurement machines
@app.route('/checkmeasurers', methods=['GET'])
def check():
    if abs(activeR - activeS) != 0:
        return 'Algunos medidores no responden!', 200
    else:
        return 'Todo OK!', 200
    
@app.route('/sendcode', methods=['POST'])
def cap_code():
    # Check if the file part is present in the request
    if 'file' not in request.files:
        print("bad request, no file")
        return 'No file part', 400

    # Retrieve the file from the request
    file = request.files['file']

    # Retrieve task_type if provided in the request
    task_type = request.form.get('task_type', '')
    input_size = request.form.get('input_size',10000)

    # Validate file and task type
    if file.filename == '':
        return 'No selected file', 400
    if not file.filename.endswith('.zip'):
        return 'Invalid file type', 400
    print("Zip package received! ")
    # Save the zip file temporarily
    temp_zip_path = "temp_upload.zip"
    file.save(temp_zip_path)

    # Process the zip file
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        cpp_dirs_onZip = []
        names_onZip = []
        fileNames = []
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.cpp'):
                # Generate a unique identifier for each .cpp file
                unique_id = str(random.randint(0, 13458345324))
                print(f"Code {unique_id} found, with task {task_type}")
                if task_type == "CAMM":
                    tag = "CAMM"
                elif task_type == "LCS":
                    tag = "LCS"
                else:
                    tag = ""  # Default tag

                # Construct the file path
                name = unique_id + tag
                cpp_file_dir = "test/" + name + ".cpp"
                outputfile = "test/" + name + ".out"
                statusfile = "status/" + name

                # Extract the .cpp file and write its content to the file system
                with open(cpp_file_dir, "w", newline="\n") as f:
                    f.writelines([line.decode('utf-8') for line in zip_ref.open(file_info)])
                
                # Write to status file
                with open(statusfile, "w", newline="\n") as st:
                    st.write('IN QUEUE')
                cpp_dirs_onZip.append(cpp_file_dir)
                names_onZip.append(name)
                fileNames.append(file_info.filename)
                # Add to queue
        queuelist.append([cpp_dirs_onZip, names_onZip, "-O3", task_type, input_size, fileNames ])

    # Remove the temporary zip file
    os.remove(temp_zip_path)

    # Respond with the names of the .cpp files added to the queue and their task type

    return jsonify({'cpp_files_queued': names_onZip, 'task_type': task_type}), 200

# Process and serve the next inline item from the queue
def serve_next_inline():
    """Process and serve the next inline item from the queue."""
    next_inline = queuelist.pop()
    print("next_inline: ", next_inline)
    for file_num in range(len(next_inline[1])):
        with open("status/" + next_inline[1][file_num], 'r') as r:
            asd = r.read()
            if asd == 'IN QUEUE':
                print(next_inline)
                slave_serve(next_inline[0][file_num], next_inline[1][file_num], next_inline[2], next_inline[4])
    for file_num in range(len(next_inline[1])): 
        error_count = 0          
        with open("status/" + next_inline[1][file_num], 'r+') as r:
            asd2 = r.read()
            if asd2 != 'ERROR: no machines available':
                print("prev-graph_results")
                print(next_inline, 'served!')
                r.seek(0)
                r.write('DONE')
                r.truncate()
            else:
                error_count+=1
                print(next_inline, 'failed: No machines available!')
    if error_count == 0:
        graph_results(next_inline[1], next_inline[5],next_inline[4])
    

# Get the number of files in the 'status' directory
def get_status_file_count():
    """Return the count of files in the 'status' directory."""
    s = subprocess.run(
        "ls status| wc -l",
        capture_output=True, universal_newlines=True, shell=True)
    return int(s.stdout)

# Identify the oldest file in the 'status' directory
def get_oldest_status_file():
    """Return the path of the oldest file in the 'status' directory."""
    s2 = subprocess.run(
        "find status -type f -printf '%T+ %p\n' | sort | head -1",
        capture_output=True, universal_newlines=True, shell=True)
    temp = s2.stdout.split()
    return temp[1]

# Remove a specified file
def remove_status_file(file_path):
    """Remove the specified file."""
    print("Removed element " + file_path + "! from status files", file=sys.stderr)
    subprocess.run(["/bin/rm", file_path], timeout=15)

# Remove the associated static file for a given status file
def remove_associated_static_file(file_path):
    """Remove the associated static file for a given status file."""
    temp2 = file_path.split('/')
    subprocess.run(["/bin/rm", "static/" + temp2[1], "-rf"], timeout=15)

@app.before_first_request
def spawner():
    th.Thread(target=queue_manager, daemon=True).start()
    
def is_queue_empty():
    """Return True if the queue list is empty, otherwise return False."""
    return not queuelist

# The main queue manager function
def queue_manager():
    """Main function to manage the queue. Runs indefinitely."""
    while True:
        # An error may occur whenever mutiple files are uploaded and the first condition happens
        if is_queue_empty():
            print('Waiting...')
            if get_status_file_count() >= 50:
                oldest_file = get_oldest_status_file()
                remove_status_file(oldest_file)
                remove_associated_static_file(oldest_file)
            time.sleep(10)
        else:
            serve_next_inline()
# agregar mensajes de error en lista de status


# Start the Flask app if the script is run as the main program
if __name__ == '__main__':
    # queue_manager_thread = th(target=queue_manager)
    # queue_manager_thread.start()
    app.run(host='0.0.0.0')
