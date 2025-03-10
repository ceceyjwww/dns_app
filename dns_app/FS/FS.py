from flask import Flask, request
import socket
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

@app.route("/register", methods=["PUT"])
def register():
    try:
        data = request.get_json()
        logger.info(f"Received registration request: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return "Bad Request", 400
        
        hostname = data.get("hostname")
        ip = data.get("ip")
        as_ip = data.get("as_ip")
        as_port = data.get("as_port")
        
        logger.info(f"Parsed data: hostname={hostname}, ip={ip}, as_ip={as_ip}, as_port={as_port}")
        
        if not all([hostname, ip, as_ip, as_port]):
            logger.error("Missing required fields")
            return "Missing fields", 400
        
        # Format the registration message according to AS expectations
        dns_registration = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10\n"
        logger.info(f"Sending DNS registration: {dns_registration}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"Connecting to AS at {as_ip}:{as_port}")
        
        try:
            # Send the registration message
            sock.sendto(dns_registration.encode("utf-8"), (as_ip, int(as_port)))
            logger.info("Registration message sent")
            
            # Wait for response with timeout
            sock.settimeout(5)
            response, addr = sock.recvfrom(1024)
            response_text = response.decode('utf-8')
            logger.info(f"Received response from {addr}: {response_text}")
            
            # If we got an empty response, that means registration was successful
            if not response_text:
                return "", 201
            else:
                logger.error(f"Unexpected response from AS: {response_text}")
                return "Server Error", 500
                
        except socket.timeout:
            logger.warning("Timeout waiting for AS response")
            return "Server Error", 500
        except Exception as e:
            logger.error(f"Error in socket operations: {str(e)}")
            return "Server Error", 500
        finally:
            sock.close()
        
    except Exception as e:
        logger.error(f"Unexpected error in register endpoint: {str(e)}")
        return "Internal Server Error", 500

@app.route("/fibonacci", methods=["GET"])
def get_fib():
    number = request.args.get("number")
    if not number:
        return "Missing 'number' parameter", 400
    
    try:
        val = int(number)
    except ValueError:
        return "Bad format: number is not an integer", 400
    
    result = fibonacci(val)
    if result is None:
        return "Invalid number", 400
    
    return str(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090) 