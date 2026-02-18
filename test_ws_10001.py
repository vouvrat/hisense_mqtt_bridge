#!/usr/bin/env python3
import websocket
import json
import time

TV_IP = "IP_TV"
PORT = 10001

def test_websocket_messages():
    """Teste différents formats de messages"""
    
    ws = websocket.create_connection(f"ws://{TV_IP}:{PORT}", timeout=5)
    print(f"✅ Connecté à ws://{TV_IP}:{PORT}\n")
    
    # Messages à tester (protocoles connus Hisense/VIDAA)
    test_messages = [
        # Format RemoteNOW
        {"action": "queryDeviceInfo"},
        {"action": "launchApp", "url": ""},
        {"action": "sendKey", "keyCode": "KEY_POWER"},
        
        # Format standard
        {"type": "request", "id": 1, "request": "get_power"},
        {"type": "command", "command": "get_volume"},
        
        # Format alternatif
        {"cmd": "get_state"},
        {"method": "get_power"},
        
        # Messages simples
        "QUERY",
        "INFO",
        "STATUS",
        '{"request":"power"}',
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_messages)}")
        print('='*60)
        
        # Conversion en JSON si dict
        if isinstance(msg, dict):
            msg_str = json.dumps(msg)
        else:
            msg_str = msg
        
        print(f"📤 Envoi: {msg_str[:100]}")
        
        try:
            ws.send(msg_str)
            ws.settimeout(2)
            
            try:
                response = ws.recv()
                print(f"📨 RÉPONSE REÇUE:")
                print(f"   {response[:300]}")
                
                # Essaye de parser en JSON
                try:
                    parsed = json.loads(response)
                    print(f"   JSON: {json.dumps(parsed, indent=2)[:300]}")
                except:
                    pass
                    
            except websocket.WebSocketTimeoutException:
                print(f"⏱️  Timeout - pas de réponse")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        time.sleep(0.5)
    
    ws.close()
    print("\n" + "="*60)
    print("✅ Tests terminés")

print("="*60)
print(f"🔍 TEST WEBSOCKET PORT 10001")
print("="*60)
test_websocket_messages()