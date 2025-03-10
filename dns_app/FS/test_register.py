import requests
import json

def test_registration():
    url = "http://localhost:9090/register"
    headers = {"Content-Type": "application/json"}
    data = {
        "hostname": "fibonacci.com",
        "ip": "172.18.0.2",
        "as_ip": "10.9.10.2",
        "as_port": 30001
    }
    
    print(f"Sending registration request to {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    response = requests.put(url, headers=headers, json=data)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

if __name__ == "__main__":
    test_registration() 