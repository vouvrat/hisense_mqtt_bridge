#!/usr/bin/env python3
import websocket
import time

TV_IP = "1IP_TV"
PORT = 10001

def test_binary_handshake():
    ws = websocket.create_connection(f"ws://{TV_IP}:{PORT}", timeout=5)
    print(f"✅ Connecté\n")
    
    # Essaye d'envoyer des séquences binaires (handshakes connus)
    test_sequences = [
        b'\x00\x01\x00\x00',  # Handshake simple
        b'\x01\x00\x00\x00',  # Alternatif
        b'HELO',              # ASCII
        b'\x48\x45\x4c\x4f',  # HELO en hex
        bytes([0x12, 0x34, 0x56, 0x78]),  # Séquence test
    ]
    
    for i, seq in enumerate(test_sequences, 1):
        print(f"Test {i}: Envoi {seq.hex()} ({seq})")
        try:
            ws.send(seq, opcode=websocket.ABNF.OPCODE_BINARY)
            ws.settimeout(2)
            try:
                response = ws.recv()
                print(f"  📨 RÉPONSE: {response[:100]}")
                print(f"  📨 HEX: {response.hex()[:100] if isinstance(response, bytes) else 'N/A'}")
            except:
                print(f"  ⏱️  Pas de réponse")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
        time.sleep(0.5)
    
    ws.close()

test_binary_handshake()