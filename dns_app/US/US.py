from flask import Flask, request, jsonify
import requests
import socket
import dns.resolver

app = Flask(__name__)

registered_info = {
    "hostname": None,
    "ip": None,
    "as_ip": None,
    "as_port": None
}

def fibonacci(n):
    n_int = int(n)
    if n_int < 0:
        return None
    if n_int == 0:
        return 0
    elif n_int == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n_int + 1):
        a, b = b, a + b
    return b

def resolve_hostname(hostname, as_ip, as_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_query = f"TYPE=A\nNAME={hostname}\nVALUE=\nTTL=10\n"
        sock.sendto(dns_query.encode("utf-8"), (as_ip, int(as_port)))
        data, _ = sock.recvfrom(1024)
        response = data.decode("utf-8")
        
        for line in response.split('\n'):
            if line.startswith('VALUE='):
                return line.split('=')[1]
        return None
    except Exception as e:
        print(f"Error in DNS resolution: {e}")
        return None
    finally:
        sock.close()

@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json()
    if not data:
        return "Bad Request", 400
    
    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")
    
    if not all([hostname, ip, as_ip, as_port]):
        return "Missing fields", 400
    
    registered_info["hostname"] = hostname
    registered_info["ip"] = ip
    registered_info["as_ip"] = as_ip
    registered_info["as_port"] = as_port

    dns_registration = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(dns_registration.encode("utf-8"), (as_ip, 53533))
    except Exception as e:
        print("Error in sending DNS registration", e)
        return "Server Error", 500
    finally:
        sock.close()

    return "", 201

@app.route("/fibonacci", methods=["GET"])
def get_fib():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")
    
    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Missing required parameters", 400
    
    try:
        val = int(number)
    except ValueError:
        return "Bad format: number is not an integer", 400
    
    fs_ip = resolve_hostname(hostname, as_ip, as_port)
    if not fs_ip:
        return "Failed to resolve hostname", 500
    
    try:
        response = requests.get(f"http://{fs_ip}:{fs_port}/fibonacci?number={val}")
        if response.status_code == 200:
            return response.text, 200
        return f"Error from Fibonacci Server: {response.text}", response.status_code
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Fibonacci Server: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080) 