import socket
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DNS_FILE = "dns_records.json"

def load_dns_records():
    if os.path.exists(DNS_FILE):
        with open(DNS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_dns_records(records):
    with open(DNS_FILE, 'w') as f:
        json.dump(records, f)

def parse_dns_message(message):
    records = {}
    for line in message.split('\n'):
        if not line:
            continue
        try:
            key, value = line.split('=', 1)
            records[key] = value
        except ValueError:
            logger.error(f"Invalid line format: {line}")
            continue
    return records

def create_dns_response(records):
    if 'VALUE' in records:
        return f"TYPE={records['TYPE']}\nNAME={records['NAME']}\nVALUE={records['VALUE']}\nTTL={records['TTL']}\n"
    return f"TYPE={records['TYPE']}\nNAME={records['NAME']}\nVALUE=\nTTL=10\n"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 53533))
    logger.info("AS server started on port 53533")
    
    dns_records = load_dns_records()
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            logger.info(f"Received message from {addr}: {message}")
            
            records = parse_dns_message(message)
            if not records:
                logger.error("Failed to parse DNS message")
                continue
            
            if 'VALUE' in records:
                # This is a registration request
                logger.info(f"Registration request for {records['NAME']} -> {records['VALUE']}")
                dns_records[records['NAME']] = records
                save_dns_records(dns_records)
                response = ""
            else:
                # This is a DNS query
                logger.info(f"DNS query for {records['NAME']}")
                if records['NAME'] in dns_records:
                    response = create_dns_response(dns_records[records['NAME']])
                    logger.info(f"Found record: {response}")
                else:
                    response = create_dns_response(records)
                    logger.info("No record found")
            
            sock.sendto(response.encode('utf-8'), addr)
            logger.info(f"Sent response to {addr}: {response}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            continue

if __name__ == "__main__":
    main() 