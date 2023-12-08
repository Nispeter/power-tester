import socket
import json
import subprocess as sub
import time
#from slave_utils import *

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50000        # The port used by the server

def connect_to_server(host, port):
    """Establish connection to a server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            s.connect((host, port))
            return s
        except ConnectionRefusedError:
            print('Waiting for connection')
            time.sleep(5)

def receive_payload(s):
    """Receive and decode payload from the server."""
    payload = b''
    while True:
        try:
            data = s.recv(1024)
            if not data:
                break
            payload += data
        except ConnectionResetError:
            break
    return json.loads(payload.decode())

def write_code_to_file(name_request, code):
    """Write received code to a .cpp file."""
    name = name_request + ".cpp"
    with open(name, 'w') as f:
        f.write(code)
    return name

def compile_and_execute(name):
    """Compile and execute the code."""
    sub.run(["g++", name], universal_newlines=True)
    try:
        aux = sub.run(["bash", "measurescript2.sh", "a.out"], capture_output=True, universal_newlines=True, timeout=45)
    except sub.TimeoutExpired:
        return ""
    return aux.stdout.strip()

def cae_lcs(name, input_size):
    """Compile and execute the code with varying input sizes."""
    sub.run(["g++", name], universal_newlines=True)
    try:
        aux = sub.run(["bash", "measurescript4.sh", "./a.out", "./input/english.50MB", str(input_size)], capture_output=True, universal_newlines=True, timeout=3000)
    except sub.TimeoutExpired:
        return "time out"
    return aux.stdout.strip()


def cae_camm(name, input_size):
    # Insert any customizations specific to CAMM tasks if needed
    print("input size:  ", input_size)
    sub.run(["g++", name], universal_newlines=True)
    print("running: ", name)
    try:
        aux = sub.run(["bash", "measurescript3.sh", "./a.out", "./input/numerical_input.txt", str(input_size)], capture_output=True, universal_newlines=True, timeout=3000)
    except sub.TimeoutExpired:
        return "time out"
    return aux.stdout.strip()

def cae_size(name, input_size):
    # Insert any customizations specific to CAMM tasks if needed
    print("input size:  ", input_size)
    sub.run(["g++", name], universal_newlines=True)
    print("running: ", name)
    try:
        aux = sub.run(["bash", "measurescript5.sh", "./a.out", str(input_size)], capture_output=True, universal_newlines=True, timeout=3000)
    except sub.TimeoutExpired:
        return "time out"
    return aux.stdout.strip()

def send_results(host, port, name_request, result_name):
    """Send the results to the server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect((host, port))
        with open(result_name, 'r') as f:
            results = f.read()
        payload = {"name": name_request + "Results", "results": results}
        s2.sendall(json.dumps(payload).encode())

def cleanup_files(*files):
    """Remove specified files."""
    sub.run(["rm"] + list(files), timeout=15)

    

def main():
    while True:
        # Connect to the server and receive payload
        with connect_to_server(HOST, PORT) as s:
            payload_dict = receive_payload(s)
        
        if "LCS" in payload_dict["name"]:
            print('Received LCS', payload_dict["name"])
            filename = write_code_to_file(payload_dict["name"], payload_dict["code"])
            input_size = payload_dict["input_size"]
            result_name = cae_lcs(filename, input_size)
            cleanup_files(filename, 'a.out')

        elif "SIZE" in payload_dict["name"]:
            print('Received SIZE', payload_dict["name"])
            filename = write_code_to_file(payload_dict["name"], payload_dict["code"])
            input_size = payload_dict["input_size"]
            result_name = cae_size(filename, input_size)  
            cleanup_files(filename, 'a.out')
            
        elif "CAMM" in payload_dict["name"]:  # Handle CAMM submissions
            print('Received CAMM', payload_dict["name"])
            filename = write_code_to_file(payload_dict["name"], payload_dict["code"])
            input_size = payload_dict["input_size"]
            result_name = cae_camm(filename, input_size)  # Call the CAMM function
            cleanup_files(filename, 'a.out')

        else:
            print('Received', payload_dict["name"])
            filename = write_code_to_file(payload_dict["name"], payload_dict["code"])
            result_name = compile_and_execute(filename)
            cleanup_files(filename, 'a.out')

        # Send the results back to the server
        send_results(HOST, 60000, payload_dict["name"], result_name)
        print('Sent', payload_dict["name"] + "Results")
        
        time.sleep(10)

if __name__ == "__main__":
    main()

