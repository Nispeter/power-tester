import socket, json, time

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


#ejecutar script de pruebas

PORT2 = 60000

time.sleep(2)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
    s2.connect((HOST, PORT2))
    with open("ejemplo.txt", 'r') as f:
        results = f.read()
    m = {"name": nameRequest + "Results", "results": results}
    json_string = json.dumps(m)
    s2.sendall(json_string.encode())

print('Sent', m["name"])
