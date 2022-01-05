# , make_response , send_file
from flask import Flask, request, render_template, abort
from flask_cors import CORS
import matplotlib.pyplot as plt
import csv
import subprocess
import random
import time
import socket
import json
import threading as th


app = Flask(__name__)

CORS(app)


def graph_results(name, thd):

    thd.join()
    nameresult = name + "Results"
    x = []
    y = []
    i = 1
    print("Plotting!")
    subprocess.run(["mkdir", "static/" + name], universal_newlines=True)
    with open(nameresult, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        titleRow = next(lines)
        title = titleRow[12]
        for row in lines:
            x.append(i)
            i = i + 1
            y.append(int(row[12]))
    plt.plot(x, y, color='g', linestyle='dashed', marker='o', label="Test")
    # plt.xticks(rotation = 25)
    plt.xlabel("Iteracion")
    plt.ylabel(title)
    plt.minorticks_on()
    plt.title('Ciclos', fontsize=20)
    plt.grid()
    plt.legend()
    aux = str(1)
    plt.savefig("static/" + name + "/fig" + aux + ".svg", format='svg')


def send_manager(s, json_string):
    firsttime = True
    while True:
        try:
            conn, addr = s.accept()  # romper loop con s.accept de otro puerto
            th.Thread(target=send_program, args=(conn, json_string)).start()
        except socket.timeout:
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
    # usar return para ver cantidad de medidores disponibles (?)


def send_program(conn, json_string):
    with conn:
        conn.sendall(json_string.encode())


def recv_manager(s):
    firsttime = True
    while True:
        try:
            conn, addr = s.accept()
            th.Thread(target=receive_data, args=(conn, )).start()
        except socket.timeout:
            break
        if(firsttime):
            firsttime = False
            s.settimeout(5.0)
        # inicia conteo de 5 segundos para recibir archivos


def receive_data(conn):
    with conn:
        payload = b''
        while True:
            data = conn.recv(1024)
            if not data:
                break
            payload += data
        payloadDict = json.loads(payload.decode())
        name = payloadDict["name"]
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


def security_check(file_dir):
    pass


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


'''@app.route('/image', methods=['GET'])
def image():
    return send_file("static/favicon.ico", mimetype="image/gif")'''


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
    # ftp = FTP(host='192.168.56.101', user='diego', passwd='holahola01k')  #Cambiar para utilizar lista de ips de esclavos. Red local, no es necesario proteger passwd
    # ftp.cwd('Desktop')
    # f = open(file_dir, 'rb')
    # ftp.storlines('STOR '+ file_dir2 + '.cpp', f)
    # ftp.quit()
    if not security_check:
        abort(409)
    new_compile = subprocess.Popen(["g++", file_dir, "-o", outputfile],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    try:
        new_compile.wait(timeout=15)
    except subprocess.TimeoutExpired:
        new_compile.kill()
    outputfile = "./" + outputfile
    new_execute = subprocess.Popen(
        [outputfile], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    try:
        output, outerr = new_execute.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        new_execute.kill()
        output, outerr = new_execute.communicate()

    # newpid = os.fork()
    # if newpid == 0:
    print("Code received!")
    aux = th.Thread(target=slave_serve, args=(file_dir, name, "-O3", ))
    aux.start()
    aux2 = th.Thread(target=graph_results, args=(name, aux, ))
    aux2.start()
    #    os._exit(0)
    return '<h1>200 OK</h1>', 200
