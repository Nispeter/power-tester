import socket, json

HOST = '192.168.56.1'  # The server's hostname or IP address
PORT = 50000        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    payload = s.recv(1024)
    payloadDict = json.loads(payload.decode())
    name = payloadDict["name"] + ".cpp"
    with open(name, 'w') as f:
        f.write(payloadDict["code"])

print('Received', payloadDict["name"])