# , make_response , send_file
from flask import Flask, request, render_template, abort
from flask_cors import CORS
#from werkzeug.exceptions import HTTPException
#from ftplib import FTP
import subprocess
import random
import time
import socket
import json
import threading as th


app = Flask(__name__)

CORS(app)


def countdown(time_sec):
    while time_sec:
        time.sleep(1)
        time_sec -= 1


def send_program(conn, addr, json_string):
    with conn:
        conn.sendall(json_string.encode())


def receive_data(conn, addr, s):
    with s:
        payload = b''
        while True:
            data = s.recv(1024)
            if not data:
                break
            payload += data
        payloadDict = json.loads(payload.decode())
        name = payloadDict["name"]
        with open(name, 'w') as f:
            f.write(payloadDict["results"])


def slave_serve(file_dir, name, cmd):
    port = 50000
    host = '192.168.56.1'
    print(file_dir, name, cmd)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #   s.setblocking(False)
        s.settimeout(5.0)
        s.bind((host, port))
        s.listen(5)
        with open(file_dir, 'r') as f:
            code = f.read()
        m = {"name": name, "cmd": cmd, "code": code}
        json_string = json.dumps(m)
        aux = th.Thread(target=countdown, args=(5,))
        aux.start()
        while aux.is_alive():
            conn, addr = s.accept() #romper loop con s.accept de otro puerto
            th.Thread(target=send_program, args=(conn, addr, json_string)).start()
    #    conn.send("name="+ name.encode())
    #    conn.send(cmd.encode())

    #   l = f.read(1024)
    ''' with conn:
            while l:
                conn.send(l)
                l = f.read(1024)
            f.close()'''
    # recibir datos (?)
    port = 60000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(5.0)
        s.bind((host, port))
        s.listen(5)
        aux2 = th.Thread(target=countdown, args=(5,))
        aux2.start()
        while aux2.is_alive():
            conn, addr = s.accept()
            th.Thread(target=receive_data, args=(conn, addr, s)).start()


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
    #f = open(file_dir, 'rb')
    #ftp.storlines('STOR '+ file_dir2 + '.cpp', f)
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

    #newpid = os.fork()
    # if newpid == 0:
    slave_serve(file_dir, name, "-O3")
    #    os._exit(0)
    return '<h1>200 OK</h1>', 200
