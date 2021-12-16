import socket
import json
import time
import subprocess as sub

HOST = '192.168.56.1'  # The server's hostname or IP address
PORT = 50000        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    payload = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        payload += data
    payloadDict = json.loads(payload.decode())
    nameRequest = payloadDict["name"]
    name = nameRequest + ".cpp"
    with open(name, 'w') as f:
        f.write(payloadDict["code"])

print('Received', payloadDict["name"])


# ejecutar script de pruebas
sub.run(["g++", name], universal_newlines=True)
try:
    aux = sub.run(["bash", "measurescript.sh", "a.out"], capture_output=True, universal_newlines=True, timeout=15)
except s.TimeoutExpired:
    # ver que hacer en caso de error
    pass
resultname = aux.stdout
resultname = resultname.strip()

PORT2 = 60000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
    s2.connect((HOST, PORT2))
    with open(resultname, 'r') as f:
        results = f.read()
    m = {"name": nameRequest + "Results", "results": results}
    json_string = json.dumps(m)
    s2.sendall(json_string.encode())

print('Sent', m["name"])

sub.run(["rm", resultname], timeout=15)
