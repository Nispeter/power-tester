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
#import os

# Initialize the Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Create an empty list to store measurement queue items
queuelist = []
# statusdict = OrderedDict()

# Initialize variables to keep track of active measurement machines
activeS = 0  # medidores activos (medidores que han respondido al servidor)
activeR = 0

# Define colors, units of measurement, and titles for graphs
color = ['red', 'green', 'blue', 'orange', 'purple']
unidadesdemedida = ['Joules', 'Joules', 'Joules', 'Instrucciones', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Lecturas', 'Fallos', 'Escrituras', 'Fallos', 'Referencias', 'Saltos', 'Fallos', 'Ciclos', 'Nanosegundos']
titulos = ['Energía de Nucleos', 'Energía de Paquete', 'Energía de RAM', 'Instrucciones', 'Lecturas de LLC', 'Fallos de lectura de LLC', 'Escrituras de LLC', 'Fallas de escritura de LLC', 'Lecturas de L1D', 'Fallas de lectura de L1D', 'Escrituras de L1D', 'Fallos de caché', 'Referencias de caché', 'Saltos', 'Fallas en saltos', 'Ciclos de CPU', 'Tiempo de ejecución']

# Define routes and their respective functions
# Function to plot and save graphs from measurement results
def create_directory(name):
    print("Creating directory for " + name + "!")
    subprocess.run(["/bin/mkdir", "static/" + name], universal_newlines=True)

def read_csv_data(name):
    nameresult = name + "Results" + str(0) + ".csv"
    return pd.read_csv(nameresult)

def calculate_normalized_power(csvobj):
    for i in range(3):
        aux2 = []
        for j in range(30):
            print(j)
            temp = csvobj.iloc[j, 16] / float(10**9)
            temp2 = csvobj.iloc[j, i] / temp
            temp2 = round(temp2, 3)
            aux2.append(temp2)
        if i == 0:
            csvobj['PowerCores'] = aux2
        if i == 1:
            csvobj['PowerPkg'] = aux2
        if i == 2:
            csvobj['PowerRAM'] = aux2
    return csvobj

def save_normalized_data(name, csvobj):
    with open("static/"+name+"/"+name+"ResultsFinal.csv", 'x') as w:
        csvobj.to_csv(w, index=False)

def plot_graphs(name, csvobj):
    nameresult = name + "Results" + str(0) + ".csv"
    for columni in range(17):
        fig, ax = plt.subplots()
        df = csvobj
        test = csvobj.iloc[:, columni]
        if(columni < 3):
            ax2 = ax.twinx()
            test2 = csvobj.iloc[:, columni+17]
            ax.axhline(mean(test), label='Energia promedio', color='orange')
            ax2.axhline(mean(test2), label='Potencia promedio', color='purple')
            df.plot(y=columni, use_index=True, kind='bar', ax=ax, color='lightblue',
                    ylabel=unidadesdemedida[columni], legend=None, xlabel='Iteraciones', title=titulos[columni])
            ax.set_ylim(top=max(test)+0.1, bottom=max(min(test)-0.1,0))
            df.plot(y=columni+17, use_index=True, kind='line', ax=ax2, color='red', ylabel='Watts', style='--', marker='.')
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc='upper right')
            plt.xticks(np.arange(0,30, step=5))
        else:
            try:
                df.plot(
                    y=columni, use_index=True, color=color[0], title=titulos[columni],
                    legend=None, xlabel='Iteraciones',
                    ylabel=unidadesdemedida[columni], style='--', marker='.', ax=ax, label="")
                ax.axhline(mean(test), label='Promedio', color='orange')
            except TypeError:
                print("err: ",TypeError )
                continue
        if(columni>3):
            plt.ticklabel_format(scilimits=[-5,5])
        plt.minorticks_on()
        plt.grid()
        if ax.lines:
            plt.savefig("static/" + name + "/fig" + str(columni) + ".svg", format='svg')
        plt.close(fig)
    subprocess.run(["/bin/mv", nameresult, "static/" + name])
    print("Done!")

def graph_results(name):
    create_directory(name)
    csvobj = read_csv_data(name)
    csvobj = calculate_normalized_power(csvobj)
    save_normalized_data(name, csvobj)
    plot_graphs(name, csvobj)


# Function to manage sending data to measurement machines
def send_manager(s, json_string, name):
    global activeS
    firsttime = True
    s.settimeout(20.0)
    counter = 0
    while True:
        try:
            conn, addr = s.accept()
            th.Thread(target=send_program, args=(conn, json_string), daemon=True).start()
            counter = counter + 1
        except socket.timeout:
            if counter == 0:
                print("No measure machines available!", file=sys.stderr)
                w = open("status/"+name, 'r+')
                w.seek(0)
                w.write('ERROR: no machines available')
                w.truncate()
                w.close()
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
    activeS = counter

# Function to send program code to a measurement machine
def send_program(conn, json_string):
    with conn:
        conn.sendall(json_string.encode())

# Function to manage receiving data from measurement machines
def recv_manager(s, name):
    global activeR
    counter = 0
    firsttime = True
    s.settimeout(1000.0)
    while True:
        try:
            conn, addr = s.accept()
            th.Thread(target=receive_data, args=(conn, counter, ), daemon=True).start()
            counter = counter + 1
        except socket.timeout:
            if counter == 0:
                print("No measure machines available!", file=sys.stderr)
                w = open("status"+name, 'r+')
                w.seek(0)
                w.write('ERROR: no machines available')
                w.truncate()
                w.close()
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
        # inicia conteo de 5 segundos para recibir archivos
    activeR = counter

# Function to receive and process data from a measurement machine
def receive_data(conn, ident):
    with conn:
        payload = b''
        while True:
            data = conn.recv(1024)
            if not data:
                break
            payload += data
        payloadDict = json.loads(payload.decode())
        name = payloadDict["name"] + str(ident) + ".csv"
        with open(name, 'w') as f:
            f.write(payloadDict["results"])

# Function to serve as a measurement machine
def slave_serve(file_dir, name, cmd):
    port = 50_000
    port2 = 60_000
    host = '127.0.0.1'
    print(file_dir, name, cmd)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Como Gunicorn utiliza 3 trabajadores para el back-end, puede que un trabajador se encuentre con que otro esta usando un socket
    # Por lo tanto, si ocurre, el trabajador espera a que el socket se libere para poder utilizarlo
    while(True):
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s2.bind((host, port2))
            s.listen(5)
            s2.listen(5)
            with open(file_dir, 'r') as f:
                code = f.read()
            m = {"name": name, "cmd": cmd, "code": code}
            json_string = json.dumps(m)
            sendmng = th.Thread(target=send_manager, args=(s, json_string, name, ), daemon=True)
            sendmng.start()
            recvmng = th.Thread(target=recv_manager, args=(s2, name, ), daemon=True)
            recvmng.start()
            sendmng.join()
            print("Socket 1 disconnected!")
            recvmng.join()
            print("Socket 2 disconnected!")
            s.close()
            s2.close()
            break
        except OSError:
            time.sleep(1)
            #print('waiting for sock', os.getpid())

# Function to perform a security check before executing received code (Placeholder)
def security_check():
    pass


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
