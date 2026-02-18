#!/usr/bin/env python3
import requests
import json

TV_IP = "IP_TV"
PORT = 9080

def test_endpoint(path, method="GET", data=None):
    """Teste un endpoint de l'API"""
    url = f"http://{TV_IP}:{PORT}{path}"
    print(f"\n{'='*60}")
    print(f"{method} {url}")
    print('='*60)
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=3)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=3)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text[:500]}")
        
        try:
            print(f"JSON: {json.dumps(response.json(), indent=2)}")
        except:
            pass
            
        return response
    except Exception as e:
        print(f"Erreur: {e}")
        return None

# ENDPOINTS À TESTER
endpoints = [
    "/",
    "/status",
    "/state",
    "/api",
    "/api/v1",
    "/info",
    "/device",
    "/tv",
    "/power",
    "/volume",
    "/input",
    "/apps",
    "/remote",
    "/commands"
]

print("="*60)
print(f"🔍 TEST API HTTP sur {TV_IP}:{PORT}")
print("="*60)

for endpoint in endpoints:
    test_endpoint(endpoint)

# Teste aussi des commandes POST
print("\n" + "="*60)
print("📤 TEST COMMANDES POST")
print("="*60)

commands = [
    ("/power", {"action": "get"}),
    ("/volume", {"action": "get"}),
    ("/state", {"action": "get"}),
    ("/remote", {"key": "POWER"}),
]

for path, data in commands:
    test_endpoint(path, method="POST", data=data)