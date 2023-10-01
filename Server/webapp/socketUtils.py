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

# Initialize variables to keep track of active measurement machines
activeS = 0  # medidores activos (medidores que han respondido al servidor)
activeR = 0

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
