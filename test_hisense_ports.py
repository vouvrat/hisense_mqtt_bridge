#!/usr/bin/env python3
import websocket
import requests
import time
import json

TV_IP = "IP_TV"
PORTS = [36668, 36669, 7681, 56789, 56790, 9080, 38400, 10001]

def test_websocket(port):
    """Teste WebSocket sur un port"""
    print(f"\n🔌 Test WebSocket ws://{TV_IP}:{port}")
    try:
        ws = websocket.create_connection(
            f"ws://{TV_IP}:{port}", 
            timeout=3
        )
        print(f"  ✅ Connexion WebSocket RÉUSSIE!")
        
        # Essaye différents messages
        test_messages = [
            '{"action":"getState"}',
            '{"cmd":"ui_service","action":"gettvstate"}',
            '{"type":"request","id":1,"method":"get_power"}',
            'HELLO'
        ]
        
        for msg in test_messages:
            try:
                print(f"  📤 Envoi: {msg[:50]}")
                ws.send(msg)
                ws.settimeout(2)
                response = ws.recv()
                print(f"  📨 RÉPONSE: {response[:200]}")
                ws.close()
                return True
            except:
                pass
        
        ws.close()
        print(f"  ⚠️  Pas de réponse aux messages de test")
        return True  # Mais connexion OK
        
    except Exception as e:
        print(f"  ❌ Échec: {str(e)[:80]}")
        return False

def test_http(port):
    """Teste HTTP sur un port"""
    print(f"\n🌐 Test HTTP http://{TV_IP}:{port}")
    try:
        response = requests.get(
            f"http://{TV_IP}:{port}", 
            timeout=3
        )
        print(f"  ✅ HTTP {response.status_code}")
        print(f"  📄 Contenu: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"  ❌ Échec: {str(e)[:80]}")
        return False

def test_ssl_websocket(port):
    """Teste WebSocket SSL sur un port"""
    print(f"\n🔒 Test WebSocket SSL wss://{TV_IP}:{port}")
    try:
        ws = websocket.create_connection(
            f"wss://{TV_IP}:{port}",
            timeout=3,
            sslopt={"cert_reqs": 0}
        )
        print(f"  ✅ Connexion SSL RÉUSSIE!")
        ws.close()
        return True
    except Exception as e:
        print(f"  ❌ Échec: {str(e)[:80]}")
        return False

# MAIN
print("="*60)
print(f"🔍 SCAN COMPLET DE {TV_IP}")
print("="*60)

working_ports = []

for port in PORTS:
    print(f"\n{'='*60}")
    print(f"Port {port}")
    print(f"{'='*60}")
    
    if test_websocket(port):
        working_ports.append((port, "WebSocket"))
    
    time.sleep(0.5)
    
    if test_http(port):
        working_ports.append((port, "HTTP"))
    
    time.sleep(0.5)
    
    if test_ssl_websocket(port):
        working_ports.append((port, "WebSocket SSL"))
    
    time.sleep(0.5)

# RÉSUMÉ
print("\n" + "="*60)
print("📊 RÉSUMÉ")
print("="*60)
if working_ports:
    print("\n✅ PORTS FONCTIONNELS:")
    for port, proto in working_ports:
        print(f"   • Port {port}: {proto}")
else:
    print("\n❌ Aucun port ne répond")

print("\n" + "="*60)