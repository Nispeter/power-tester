# , make_response , send_file
# Import necessary modules and libraries
from flask import Flask, request, render_template, abort, url_for, redirect, make_response, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import random
import socket
import json
import threading as th
import time
from statistics import mean
import sys
import numpy as np
from dataProcessing import *
from socketUtils import *
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
# crear ruta para ver status de codigo
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

@app.route('/submit/lcs', methods=['POST'])
def submit_lcs_solution():
    code = request.form['code']
    
    # Prepare the directory and status files similarly to /sendcode
    file_dir = str(random.randint(0, 13458345324))+"LCS"
    name = file_dir
    outputfile = "test/" + file_dir + ".out"
    file_dir = "test/" + file_dir + ".cpp"
    
    # Write the received code to a file
    with open(file_dir, "w", newline="\n") as f:
        f.write(code)
        
    statusfile = "status/" + name
    st = open(statusfile, "w", newline="\n")
    time.sleep(2)
    print("LCS Code received!")
    new_compile = subprocess.Popen(
        ["g++", file_dir, "-o", outputfile],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    try:    
        output, outerr = new_compile.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        new_compile.kill()
        st.write('ERROR: timeout compile\n')
        st.write(outerr)
        st.close()
        return str(name), 200
    if new_compile.returncode:
        st.write('ERROR: at compile\n')
        st.write(outerr)
        st.close()
        return str(name), 200
    
    # Clean up and queue
    subprocess.run(["/bin/rm", outputfile], timeout=15)
    
    # This is where we differentiate from the /sendcode
    # Adding an LCS indication to the payload
    queuelist.append([file_dir, name, "-O3"])
    st.write('IN QUEUE')
    st.close()
    
    return str(name), 200

# Route to receive and process code from clients
@app.route('/sendcode', methods=['POST'])          # endpoint Recibir Codigo
def cap_code():
    code = request.form['code']
    file_dir = str(random.randint(0, 13458345324))
    name = file_dir
    outputfile = "test/" + file_dir + ".out"
    file_dir = "test/" + file_dir + ".cpp"
    with open(file_dir, "w", newline="\n") as f:
        f.write(code)
    statusfile = "status/" + name
    st = open(statusfile, "w", newline="\n")
    time.sleep(2)
    print("Code received!")
    if not security_check:
        abort(409)
    # temppath = 'g++ ' + file_dir + ' -o ' + outputfile
    # print(temppath)
    new_compile = subprocess.Popen(
       ["g++", file_dir, "-o", outputfile],
       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    try:
        output, outerr = new_compile.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        new_compile.kill()
        st.write('ERROR: timeout compile\n')
        st.write(outerr)
        st.close()
        return str(name), 200
    if new_compile.returncode:
        st.write('ERROR: at compile\n')
        st.write(outerr)
        st.close()
        return str(name), 200
    #outputfile = "./" + outputfile
    #new_execute = subprocess.Popen(
    #    [outputfile], stdin=subprocess.PIPE,
    #    stdout=subprocess.PIPE, universal_newlines=True)
    #try:
    #    output, outerr = new_execute.communicate(timeout=15)
    #except subprocess.TimeoutExpired:
    #    new_execute.kill()
    #    output, outerr = new_execute.communicate()
    #    st.write('ERROR: timeout execute\n')
    #    st.write(outerr)
    #    st.close()
    #    return str(name), 200
    #if new_execute.returncode:
    #    st.write('ERROR: execute returned non-zero\n')
    #    return str(name), 200
    #else:
    subprocess.run(["/bin/rm", outputfile], timeout=15)
    queuelist.append([file_dir, name, "-O3"])
    st.write('IN QUEUE')
    st.close()
    # print(statusdict, len(statusdict))
    return str(name), 200

# Function to run the queue manager thread
@app.before_first_request
def spawner():
    th.Thread(target=queue_manager, daemon=True).start()

# Queue manager function to handle the execution queue

# Check if the queue is empty
def is_queue_empty():
    """Return True if the queue list is empty, otherwise return False."""
    return not queuelist

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

# Process and serve the next inline item from the queue
def serve_next_inline():
    """Process and serve the next inline item from the queue."""
    next_inline = queuelist.pop()
    with open("status/" + next_inline[1], 'r') as r:
        asd = r.read()
        if asd == 'IN QUEUE':
            print(next_inline)
            slave_serve(next_inline[0], next_inline[1], next_inline[2])
            with open("status/" + next_inline[1], 'r+') as r:
                asd2 = r.read()
                if asd2 != 'ERROR: no machines available':
                    print("prev-graph_results")
                    graph_results(next_inline[1])
                    print(next_inline, 'served!')
                    r.seek(0)
                    r.write('DONE')
                    r.truncate()
                else:
                    print(next_inline, 'failed: No machines available!')

# The main queue manager function
def queue_manager():
    """Main function to manage the queue. Runs indefinitely."""
    while True:
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
    app.run(host='0.0.0.0')
