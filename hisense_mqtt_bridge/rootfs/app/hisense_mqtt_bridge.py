#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import logging
import ssl
import socket
import asyncio
from threading import Thread
from datetime import datetime

import paho.mqtt.client as mqtt
import websocket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# Configuration depuis les variables d'environnement
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_USER = os.getenv('MQTT_USER', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', 'hisense_tv')
TV_IP = os.getenv('TV_IP', '')
TV_NAME = os.getenv('TV_NAME', 'salon')
SSL_ENABLED = os.getenv('SSL_ENABLED', 'true').lower() == 'true'
AUTO_DISCOVERY = os.getenv('AUTO_DISCOVERY', 'true').lower() == 'true'
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', '30'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info').upper()

# Configuration du logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HisenseMQTTBridge')

# Validation immédiate
if not TV_IP:
    logger.error("TV_IP non défini!")
    logger.error("Variables d'environnement disponibles:")
    for key, value in os.environ.items():
        if 'TV' in key or 'MQTT' in key:
            logger.error(f"  {key}={value}")
    sys.exit(1)

logger.info(f"Configuration chargée - TV IP: {TV_IP}")

class HisenseTV:
    """Classe pour gérer la communication avec la TV Hisense"""
    
    def __init__(self, ip_address, use_ssl=True):
        self.ip = ip_address
        self.use_ssl = use_ssl
        default_port = 36669 if use_ssl else 36670
        self.port = int(os.getenv('TV_PORT', str(default_port)))
        self.ws = None
        self.connected = False
        self.mac_address = None
        self.device_id = None
        
        # Clés de chiffrement (à adapter selon le modèle)
        self.key = b'0000000000000000'
        self.iv = b'0000000000000000'
        
        # État de la TV
        self.state = {
            'power': 'OFF',
            'volume': 0,
            'muted': False,
            'source': None,
            'channel': None,
            'app': None
        }
        
    def connect(self):
        """Connexion WebSocket à la TV"""
        try:
            protocol = "wss" if self.use_ssl else "ws"
            url = f"{protocol}://{self.ip}:{self.port}"
            
            logger.info(f"Connexion à la TV: {url}")
            
            if self.use_ssl:
                self.ws = websocket.WebSocketApp(
                    url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )
                self.ws.run_forever(
                    sslopt={
                        "cert_reqs": ssl.CERT_NONE,
                        "check_hostname": False,
                        "ssl_version": ssl.PROTOCOL_TLSv1_2
                    }
                )
            else:
                self.ws = websocket.WebSocketApp(
                    url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )
                self.ws.run_forever()
                
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
            self.connected = False
            
    def _on_open(self, ws):
        """Callback lors de l'ouverture de la connexion"""
        logger.info("Connexion WebSocket établie")
        self.connected = True
        self._authenticate()
        
    def _on_message(self, ws, message):
        """Callback lors de la réception d'un message"""
        try:
            logger.debug(f"Message reçu: {message}")
            data = json.loads(message)
            self._process_message(data)
        except json.JSONDecodeError:
            logger.warning(f"Message non-JSON reçu: {message}")
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            
    def _on_error(self, ws, error):
        """Callback en cas d'erreur"""
        logger.error(f"Erreur WebSocket: {error}")
        self.connected = False
        
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback lors de la fermeture"""
        logger.warning(f"Connexion fermée: {close_status_code} - {close_msg}")
        self.connected = False
        
    def _authenticate(self):
        """Authentification avec la TV"""
        try:
            # Handshake initial
            handshake = {
                "action": "handshake",
                "type": "request"
            }
            self._send_command(handshake)
            
        except Exception as e:
            logger.error(f"Erreur d'authentification: {e}")
            
    def _encrypt_payload(self, payload):
        """Chiffrement du payload avec AES"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            padded = pad(payload.encode(), AES.block_size)
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erreur de chiffrement: {e}")
            return None
            
    def _decrypt_payload(self, encrypted_payload):
        """Déchiffrement du payload"""
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decoded = base64.b64decode(encrypted_payload)
            decrypted = cipher.decrypt(decoded)
            unpadded = unpad(decrypted, AES.block_size)
            return unpadded.decode()
        except Exception as e:
            logger.error(f"Erreur de déchiffrement: {e}")
            return None
            
    def _send_command(self, command):
        """Envoi d'une commande à la TV"""
        if not self.connected or not self.ws:
            logger.warning("TV non connectée, impossible d'envoyer la commande")
            return False
            
        try:
            message = json.dumps(command)
            logger.debug(f"Envoi commande: {message}")
            self.ws.send(message)
            return True
        except Exception as e:
            logger.error(f"Erreur envoi commande: {e}")
            return False
            
    def _process_message(self, data):
        """Traitement des messages reçus de la TV"""
        try:
            action = data.get('action')
            msg_type = data.get('type')
            
            if action == 'handshake' and msg_type == 'response':
                logger.info("Handshake réussi")
                self._request_state()
                
            elif action == 'state':
                # Mise à jour de l'état
                if 'power' in data:
                    self.state['power'] = 'ON' if data['power'] else 'OFF'
                if 'volume' in data:
                    self.state['volume'] = data['volume']
                if 'mute' in data:
                    self.state['muted'] = data['mute']
                if 'sourceid' in data:
                    self.state['source'] = data['sourceid']
                    
                logger.debug(f"État mis à jour: {self.state}")
                
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            
    def _request_state(self):
        """Demande l'état actuel de la TV"""
        command = {
            "action": "state",
            "type": "request"
        }
        self._send_command(command)
        
    def send_key(self, keycode):
        """Envoi d'une touche"""
        command = {
            "action": "sendkey",
            "type": "request",
            "keycode": keycode
        }
        return self._send_command(command)
        
    def power_on(self):
        """Allumer la TV"""
        return self.send_key("KEY_POWER")
        
    def power_off(self):
        """Éteindre la TV"""
        return self.send_key("KEY_POWER")
        
    def volume_up(self):
        """Augmenter le volume"""
        return self.send_key("KEY_VOLUMEUP")
        
    def volume_down(self):
        """Diminuer le volume"""
        return self.send_key("KEY_VOLUMEDOWN")
        
    def mute(self):
        """Couper/rétablir le son"""
        return self.send_key("KEY_MUTE")
        
    def channel_up(self):
        """Chaîne suivante"""
        return self.send_key("KEY_CHANNELUP")
        
    def channel_down(self):
        """Chaîne précédente"""
        return self.send_key("KEY_CHANNELDOWN")
        
    def set_source(self, source):
        """Changer de source"""
        source_map = {
            'HDMI1': 'KEY_HDMI1',
            'HDMI2': 'KEY_HDMI2',
            'HDMI3': 'KEY_HDMI3',
            'HDMI4': 'KEY_HDMI4',
            'TV': 'KEY_TV',
            'AV': 'KEY_AV'
        }
        
        key = source_map.get(source.upper())
        if key:
            return self.send_key(key)
        else:
            logger.warning(f"Source inconnue: {source}")
            return False
            
    def navigate(self, direction):
        """Navigation dans les menus"""
        direction_map = {
            'UP': 'KEY_UP',
            'DOWN': 'KEY_DOWN',
            'LEFT': 'KEY_LEFT',
            'RIGHT': 'KEY_RIGHT',
            'OK': 'KEY_OK',
            'BACK': 'KEY_BACK',
            'HOME': 'KEY_HOME',
            'MENU': 'KEY_MENU'
        }
        
        key = direction_map.get(direction.upper())
        if key:
            return self.send_key(key)
        else:
            logger.warning(f"Direction inconnue: {direction}")
            return False

class MQTTBridge:
    """Classe pour gérer le pont MQTT"""
    
    def __init__(self):
        self.mqtt_client = None
        self.tv = None
        self.running = False
        
        # Configuration depuis variables d'environnement
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 1883))
        self.mqtt_user = os.getenv('MQTT_USER', '')
        self.mqtt_password = os.getenv('MQTT_PASSWORD', '')
        self.topic_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'hisense_tv')
        self.tv_ip = os.getenv('TV_IP')
        self.tv_name = os.getenv('TV_NAME', 'salon')
        self.ssl_enabled = os.getenv('SSL_ENABLED', 'true').lower() == 'true'
        self.auto_discovery = os.getenv('AUTO_DISCOVERY', 'true').lower() == 'true'
        self.scan_interval = int(os.getenv('SCAN_INTERVAL', 30))
        
        # Validation
        if not self.tv_ip:
            logger.error("TV_IP non défini!")
            sys.exit(1)
            
        # Topics MQTT
        self.base_topic = f"{self.topic_prefix}/{self.tv_name}"
        self.command_topic = f"{self.base_topic}/command"
        self.state_topic = f"{self.base_topic}/state"
        self.availability_topic = f"{self.base_topic}/availability"
        
    def setup_mqtt(self):
        """Configuration du client MQTT"""
        try:
            self.mqtt_client = mqtt.Client(client_id=f"hisense_bridge_{self.tv_name}")
            
            # Authentification si nécessaire
            if self.mqtt_user and self.mqtt_password:
                self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)
                
            # Callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Last Will Testament
            self.mqtt_client.will_set(
                self.availability_topic,
                payload="offline",
                qos=1,
                retain=True
            )
            
            # Connexion
            logger.info(f"Connexion au broker MQTT: {self.mqtt_broker}:{self.mqtt_port}")
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur configuration MQTT: {e}")
            return False
            
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback connexion MQTT"""
        if rc == 0:
            logger.info("Connecté au broker MQTT")
            
            # Publication de la disponibilité
            client.publish(self.availability_topic, "online", qos=1, retain=True)
            
            # Souscription aux commandes
            client.subscribe(f"{self.command_topic}/#", qos=1)
            logger.info(f"Souscription à: {self.command_topic}/#")
            
            # Auto-discovery Home Assistant
            if self.auto_discovery:
                self._publish_discovery()
                
        else:
            logger.error(f"Échec connexion MQTT, code: {rc}")
            
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback déconnexion MQTT"""
        if rc != 0:
            logger.warning(f"Déconnexion MQTT inattendue, code: {rc}")
            
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback réception message MQTT"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Message MQTT reçu - Topic: {topic}, Payload: {payload}")
            
            # Extraction de la commande
            command = topic.replace(f"{self.command_topic}/", "")
            
            # Traitement de la commande
            self._process_command(command, payload)
            
        except Exception as e:
            logger.error(f"Erreur traitement message MQTT: {e}")
            
    def _process_command(self, command, payload):
        """Traitement des commandes MQTT"""
        if not self.tv or not self.tv.connected:
            logger.warning("TV non connectée, commande ignorée")
            return
            
        try:
            payload_lower = payload.lower()
            
            # Commandes power
            if command == "power":
                if payload_lower == "on":
                    self.tv.power_on()
                elif payload_lower == "off":
                    self.tv.power_off()
                elif payload_lower == "toggle":
                    if self.tv.state['power'] == 'ON':
                        self.tv.power_off()
                    else:
                        self.tv.power_on()
                        
            # Commandes volume
            elif command == "volume":
                if payload_lower == "up":
                    self.tv.volume_up()
                elif payload_lower == "down":
                    self.tv.volume_down()
                elif payload.isdigit():
                    # Volume spécifique (à implémenter)
                    logger.warning("Volume spécifique non supporté")
                    
            # Mute
            elif command == "mute":
                self.tv.mute()
                
            # Changement de source
            elif command == "source":
                self.tv.set_source(payload)
                
            # Chaînes
            elif command == "channel":
                if payload_lower == "up":
                    self.tv.channel_up()
                elif payload_lower == "down":
                    self.tv.channel_down()
                elif payload.isdigit():
                    # Chaîne spécifique (à implémenter)
                    logger.warning("Chaîne spécifique non supportée")
                    
            # Navigation
            elif command == "navigate":
                self.tv.navigate(payload)
                
            # Touche spécifique
            elif command == "key":
                self.tv.send_key(payload)
                
            else:
                logger.warning(f"Commande inconnue: {command}")
                
            # Publication de l'état après commande
            time.sleep(0.5)
            self._publish_state()
            
        except Exception as e:
            logger.error(f"Erreur traitement commande: {e}")
            
    def _publish_state(self):
        """Publication de l'état de la TV"""
        if not self.tv:
            return
            
        try:
            state_data = {
                'power': self.tv.state['power'],
                'volume': self.tv.state['volume'],
                'muted': self.tv.state['muted'],
                'source': self.tv.state['source'],
                'channel': self.tv.state['channel'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Publication de l'état global
            self.mqtt_client.publish(
                self.state_topic,
                json.dumps(state_data),
                qos=1,
                retain=True
            )
            
            # Publication des états individuels
            for key, value in state_data.items():
                if key != 'timestamp':
                    self.mqtt_client.publish(
                        f"{self.state_topic}/{key}",
                        str(value),
                        qos=1,
                        retain=True
                    )
                    
            logger.debug(f"État publié: {state_data}")
            
        except Exception as e:
            logger.error(f"Erreur publication état: {e}")
            
    def _publish_discovery(self):
        """Publication des entités pour Home Assistant auto-discovery"""
        logger.info("Publication de la configuration auto-discovery")
        
        device_info = {
            "identifiers": [f"hisense_tv_{self.tv_name}"],
            "name": f"Hisense TV {self.tv_name.capitalize()}",
            "manufacturer": "Hisense",
            "model": "Vidaa TV",
            "sw_version": "1.0.0"
        }
        
        # Media Player
        media_player_config = {
            "name": f"Hisense TV {self.tv_name.capitalize()}",
            "unique_id": f"hisense_tv_{self.tv_name}_media_player",
            "device": device_info,
            "state_topic": f"{self.state_topic}/power",
            "command_topic": f"{self.command_topic}/power",
            "payload_on": "ON",
            "payload_off": "OFF",
            "availability_topic": self.availability_topic,
            "icon": "mdi:television"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/media_player/{self.tv_name}/config",
            json.dumps(media_player_config),
            qos=1,
            retain=True
        )
        
        # Switch Power
        switch_config = {
            "name": f"Hisense TV {self.tv_name.capitalize()} Power",
            "unique_id": f"hisense_tv_{self.tv_name}_power",
            "device": device_info,
            "state_topic": f"{self.state_topic}/power",
            "command_topic": f"{self.command_topic}/power",
            "payload_on": "on",
            "payload_off": "off",
            "state_on": "ON",
            "state_off": "OFF",
            "availability_topic": self.availability_topic,
            "icon": "mdi:power"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/switch/{self.tv_name}_power/config",
            json.dumps(switch_config),
            qos=1,
            retain=True
        )
        
        # Sensor Volume
        volume_config = {
            "name": f"Hisense TV {self.tv_name.capitalize()} Volume",
            "unique_id": f"hisense_tv_{self.tv_name}_volume",
            "device": device_info,
            "state_topic": f"{self.state_topic}/volume",
            "availability_topic": self.availability_topic,
            "unit_of_measurement": "%",
            "icon": "mdi:volume-high"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/sensor/{self.tv_name}_volume/config",
            json.dumps(volume_config),
            qos=1,
            retain=True
        )
        
        # Switch Mute
        mute_config = {
            "name": f"Hisense TV {self.tv_name.capitalize()} Mute",
            "unique_id": f"hisense_tv_{self.tv_name}_mute",
            "device": device_info,
            "state_topic": f"{self.state_topic}/muted",
            "command_topic": f"{self.command_topic}/mute",
            "payload_on": "true",
            "payload_off": "false",
            "state_on": "True",
            "state_off": "False",
            "availability_topic": self.availability_topic,
            "icon": "mdi:volume-mute"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/switch/{self.tv_name}_mute/config",
            json.dumps(mute_config),
            qos=1,
            retain=True
        )
        
        # Sensor Source
        source_config = {
            "name": f"Hisense TV {self.tv_name.capitalize()} Source",
            "unique_id": f"hisense_tv_{self.tv_name}_source",
            "device": device_info,
            "state_topic": f"{self.state_topic}/source",
            "availability_topic": self.availability_topic,
            "icon": "mdi:video-input-hdmi"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/sensor/{self.tv_name}_source/config",
            json.dumps(source_config),
            qos=1,
            retain=True
        )
        
        logger.info("Configuration auto-discovery publiée")
        
    def setup_tv(self):
        """Configuration de la connexion TV"""
        try:
            logger.info(f"Initialisation de la TV: {self.tv_ip}")
            self.tv = HisenseTV(self.tv_ip, self.ssl_enabled)
            
            # Lancement de la connexion dans un thread séparé
            tv_thread = Thread(target=self.tv.connect, daemon=True)
            tv_thread.start()
            
            # Attente de la connexion
            timeout = 10
            start_time = time.time()
            while not self.tv.connected and (time.time() - start_time) < timeout:
                time.sleep(0.5)
                
            if self.tv.connected:
                logger.info("TV connectée avec succès")
                return True
            else:
                logger.warning("Timeout connexion TV")
                return False
                
        except Exception as e:
            logger.error(f"Erreur configuration TV: {e}")
            return False
            
    def state_monitor(self):
        """Surveillance de l'état de la TV"""
        logger.info("Démarrage de la surveillance d'état")
        
        while self.running:
            try:
                if self.tv and self.tv.connected:
                    self.tv._request_state()
                    time.sleep(1)
                    self._publish_state()
                else:
                    # Tentative de reconnexion
                    logger.warning("TV déconnectée, tentative de reconnexion...")
                    self.mqtt_client.publish(
                        self.availability_topic,
                        "offline",
                        qos=1,
                        retain=True
                    )
                    
                    if self.setup_tv():
                        self.mqtt_client.publish(
                            self.availability_topic,
                            "online",
                            qos=1,
                            retain=True
                        )
                        
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Erreur surveillance état: {e}")
                time.sleep(self.scan_interval)
                
    def run(self):
        """Démarrage du bridge"""
        logger.info("=== Démarrage de Hisense TV MQTT Bridge ===")
        
        self.running = True
        
        # Configuration MQTT
        if not self.setup_mqtt():
            logger.error("Échec configuration MQTT")
            return False
            
        # Configuration TV
        if not self.setup_tv():
            logger.error("Échec configuration TV")
            return False
            
        # Démarrage de la surveillance
        monitor_thread = Thread(target=self.state_monitor, daemon=True)
        monitor_thread.start()
        
        logger.info("Bridge démarré avec succès")
        
        # Boucle principale
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Arrêt demandé")
            self.stop()
            
        return True
        
    def stop(self):
        """Arrêt du bridge"""
        logger.info("Arrêt du bridge...")
        
        self.running = False
        
        # Publication de l'indisponibilité
        if self.mqtt_client:
            self.mqtt_client.publish(
                self.availability_topic,
                "offline",
                qos=1,
                retain=True
            )
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
        # Fermeture de la connexion TV
        if self.tv and self.tv.ws:
            self.tv.ws.close()
            
        logger.info("Bridge arrêté")

def main():
    """Fonction principale"""
    try:
        bridge = MQTTBridge()
        bridge.run()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
