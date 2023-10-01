import socket
import json
import subprocess as sub
import time

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

def lcs_test(name, code):
    # Save the user's code to a temporary file and compile it.
    with open("temporary.cpp", "w", newline="\n") as f:
        f.write(code)

    # Compile the code.
    compilation_result = subprocess.run(["g++", "temporary.cpp", "-o", "temporary.out"], capture_output=True)
    if compilation_result.returncode != 0:
        return f"Error in {name}: Compilation Error"

    # Define test cases for LCS.
    test_cases = [("abcd", "acdf"), ("xyz", "xyz"), ...]  # Add as many test cases as required.
    
    results = []
    # Iterate over each test case.
    for i, (str1, str2) in enumerate(test_cases):
        result = subprocess.run(["./temporary.out"], input=str1 + "\n" + str2, text=True, capture_output=True)
        results.append(result.stdout.strip())

    # Return a joined string of results or however you wish to format it.
    return "\n".join(results)

def main():
    while True:
        # Connect to the server and receive payload
        with connect_to_server(HOST, PORT) as s:
            payload_dict = receive_payload(s)
        
        if "LCS" in payload_dict["name"]:
            # Handle LCS task specially
            # Assuming you'll add an "lcs_test" function which compiles, runs, and tests LCS
            result_name = lcs_test(payload_dict["name"], payload_dict["code"])
        else:
            print('Received', payload_dict["name"])
            # Save the code to file and compile & execute
            filename = write_code_to_file(payload_dict["name"], payload_dict["code"])
            result_name = compile_and_execute(filename)

            # Cleanup created files
            cleanup_files(filename, 'a.out')

        # Send the results back to the server
        send_results(HOST, 60000, payload_dict["name"], result_name)
        print('Sent', payload_dict["name"] + "Results")
        
        time.sleep(10)

if __name__ == "__main__":
    main()
