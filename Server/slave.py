import socket, json

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
    name = payloadDict["name"] + ".cpp"
    with open(name, 'w') as f:
        f.write(payloadDict["code"])

print('Received', payloadDict["name"])


#ejecutar script de pruebas