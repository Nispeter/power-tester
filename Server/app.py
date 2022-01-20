# , make_response , send_file
from flask import Flask, request, render_template, abort
from flask_cors import CORS
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import random
import socket
import json
import threading as th
import time
from collections import OrderedDict


app = Flask(__name__)

CORS(app)

queuelist = []
statusdict = OrderedDict()
activeS = 0  # medidores activos (medidores que han respondido al servidor)
activeR = 0
color = ['red', 'green', 'blue', 'orange', 'purple']


def graph_results(name):
    print("Plotting!" + name)
    print(activeS, activeR)
    subprocess.run(["mkdir", "static/" + name], universal_newlines=True)
    auxList = []
    for i in range(activeR):  # agregar funcion de leer todos los csv recibidos
        nameresult = name + "Results" + str(i) + ".csv"
        auxList.append(pd.read_csv(nameresult))
    # with open(nameresult, 'r') as csvfile:
    #     lines = csv.reader(csvfile, delimiter=',')
    #     titleRow = next(lines)
    #     title = titleRow[12]
    #     for row in lines:
    #         x.append(i)
    #         i = i + 1
    #         y.append(int(row[12]))

    for columni in range(12):
        fig, ax = plt.subplots()
        for machine in range(activeR):
            df = auxList[machine]
            try:
                df.plot(
                    y=columni, use_index=True, color=color[machine], title=df.columns[columni],
                    legend=None, xlabel='Iterations',
                    ylabel="n. de " + df.columns[columni], style='--', marker='.', ax=ax, label="Maquina "+str(machine))
            except TypeError:
                continue
        ax.ticklabel_format(scilimits=[-5,5])
        plt.minorticks_on()
        plt.grid()
        if ax.lines:
            plt.savefig("static/" + name + "/fig" + str(columni) + ".svg", format='svg')
    for machine in range(activeR):
        nameresult = name + "Results"+str(machine) + ".csv"
        subprocess.run(["mv", nameresult, "static/" + name])
    print("Done!")


def send_manager(s, json_string):
    global activeS
    firsttime = True
    counter = 0
    while True:
        try:
            conn, addr = s.accept()
            th.Thread(target=send_program, args=(conn, json_string)).start()
            counter = counter + 1
        except socket.timeout:
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
    activeS = counter


def send_program(conn, json_string):
    with conn:
        conn.sendall(json_string.encode())


def recv_manager(s):
    global activeR
    counter = 0
    firsttime = True
    while True:
        try:
            conn, addr = s.accept()
            th.Thread(target=receive_data, args=(conn, counter, )).start()
            counter = counter + 1
        except socket.timeout:
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
        # inicia conteo de 5 segundos para recibir archivos
    activeR = counter


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


def slave_serve(file_dir, name, cmd):
    port = 50000
    port2 = 60000
    host = '192.168.56.1'
    print(file_dir, name, cmd)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        sendmng = th.Thread(target=send_manager, args=(s, json_string, ))
        sendmng.start()
        recvmng = th.Thread(target=recv_manager, args=(s2,))
        recvmng.start()
    finally:
        sendmng.join()
        print("Socket 1 disconnected!")
        recvmng.join()
        print("Socket 2 disconnected!")
        s.close()
        s2.close()


def security_check():
    pass


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/checkstatus/<code>', methods=['GET'])
# crear ruta para ver status de codigo
def tmr(code):
    try:
        temp = statusdict[code]
    except KeyError:
        abort(404)
    return temp, 200


@app.route('/checkmeasurers', methods=['GET'])
def check():
    if abs(activeR - activeS) != 0:
        return 'Algunos medidores no responden!', 200
    else:
        return 'Todo OK!', 200


@app.route('/sendcode', methods=['POST'])
def cap_code():
    code = request.form['code']
    file_dir = str(random.randint(0, 13458345324))
    name = file_dir
    outputfile = "test/" + file_dir + ".out"
    file_dir = "test/" + file_dir + ".cpp"
    f = open(file_dir, "w", newline="\n")
    f.write(code)
    f.close()
    print("Code received!")
    if not security_check:
        abort(409)
    new_compile = subprocess.Popen(
        ["g++", file_dir, "-o", outputfile],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    try:
        new_compile.wait(timeout=15)
    except subprocess.TimeoutExpired:
        new_compile.kill()
        statusdict[name] = 'ERROR: timeout compile'
        return str(name, 200)
    if new_compile.returncode:
        statusdict[name] = 'ERROR: at compile'
        return str(name), 200
    outputfile = "./" + outputfile
    new_execute = subprocess.Popen(
        [outputfile], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, universal_newlines=True)
    try:
        output, outerr = new_execute.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        new_execute.kill()
        output, outerr = new_execute.communicate()
        statusdict[name] = 'ERROR: timeout execute'
    if new_execute.returncode:
        statusdict[name] = 'ERROR: execute returned non-zero'
        return str(name), 200
    queuelist.append([file_dir, name, "-O3"])
    statusdict[name] = 'READY'
    # print(statusdict, len(statusdict))
    return str(name), 200


@app.before_first_request
def spawner():
    th.Thread(target=queue_manager).start()


def queue_manager():
    while True:
        if len(statusdict) >= 10:
            statusdict.popitem(last=False)
        if not queuelist:
            print('Waiting...')
            time.sleep(10)
        else:
            nextInline = queuelist.pop()
            if statusdict[nextInline[1]] == 'READY':
                slave_serve(nextInline[0], nextInline[1], nextInline[2])
                graph_results(nextInline[1])
                print(nextInline, 'served!')
                statusdict[nextInline[1]] = 'DONE'

# agregar mensajes de error en lista de status
