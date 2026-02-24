#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hisense TV MQTT Bridge - Support for Vidaa U
Communicates with Hisense VIDAA-U TVs via WebSocket and bridges to MQTT
"""

import os
import sys
import json
import time
import logging
import ssl
import socket
import hashlib
import base64
from threading import Thread
from datetime import datetime
from typing import Optional, Dict, Any

import paho.mqtt.client as mqtt
import websocket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config():
    """Load configuration from environment variables"""
    return {
        'mqtt_broker': os.getenv('MQTT_BROKER', 'localhost'),
        'mqtt_port': int(os.getenv('MQTT_PORT', '1883')),
        'mqtt_user': os.getenv('MQTT_USER', ''),
        'mqtt_password': os.getenv('MQTT_PASSWORD', ''),
        'mqtt_topic_prefix': os.getenv('MQTT_TOPIC_PREFIX', 'hisense_tv'),
        'tv_ip': os.getenv('TV_IP', ''),
        'tv_port': int(os.getenv('TV_PORT', '10001')),
        'tv_name': os.getenv('TV_NAME', 'salon'),
        'tv_ssl': os.getenv('TV_SSL', 'false').lower() == 'true',
        'auto_discovery': os.getenv('AUTO_DISCOVERY', 'true').lower() == 'true',
        'scan_interval': int(os.getenv('SCAN_INTERVAL', '30')),
        'log_level': os.getenv('LOG_LEVEL', 'INFO').upper(),
    }

CONFIG = load_config()

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=getattr(logging, CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HisenseMQTTBridge')

# ============================================================================
# VALIDATION
# ============================================================================

if not CONFIG['tv_ip']:
    logger.error("❌ TV_IP environment variable is required!")
    sys.exit(1)

logger.info(f"✅ Configuration loaded - TV IP: {CONFIG['tv_ip']}:{CONFIG['tv_port']}")

# ============================================================================
# HISENSE TV CLASS
# ============================================================================

class HisenseTV:
    """
    Manages communication with Hisense VIDAA-U TV via WebSocket.
    Supports:
    - Port 10001 (standard Vidaa-U)
    - AES-128-CBC encryption for command protocol
    - Automatic handshake and authentication
    """

    def __init__(self, ip: str, port: int = 10001, use_ssl: bool = False):
        self.ip = ip
        self.port = port
        self.use_ssl = use_ssl
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[Thread] = None
        self.connected = False
        
        # Encryption keys (Vidaa-U default)
        self.cipher_key = b'0000000000000000'
        self.cipher_iv = b'0000000000000000'
        
        # State
        self.state = {
            'power': 'OFF',
            'volume': 0,
            'muted': False,
            'source': None,
            'channel': None,
            'app': None
        }

    def connect(self) -> bool:
        """
        Connect to TV via WebSocket with automatic port discovery.
        Tests multiple ports and protocols if primary fails.
        """
        ports_to_try = [
            (self.port, self.use_ssl),  # Primary configured port
            (10001, False),              # Standard Vidaa-U
            (36669, False),              # Legacy port
            (36670, False),              # Alternative legacy
            (36870, True),               # SSL port
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_ports = []
        for port, use_ssl in ports_to_try:
            key = (port, use_ssl)
            if key not in seen:
                seen.add(key)
                unique_ports.append((port, use_ssl))
        
        for port, use_ssl in unique_ports:
            protocol = "wss" if use_ssl else "ws"
            url = f"{protocol}://{self.ip}:{port}"
            
            try:
                logger.info(f"📡 Attempting connection: {url}")
                
                self.ws = websocket.WebSocketApp(
                    url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                
                run_kwargs = {}
                if use_ssl:
                    run_kwargs['sslopt'] = {
                        "cert_reqs": ssl.CERT_NONE,
                        "check_hostname": False,
                        "ssl_version": ssl.PROTOCOL_TLSv1_2
                    }
                
                self.ws_thread = Thread(
                    target=self.ws.run_forever,
                    kwargs=run_kwargs,
                    daemon=True
                )
                self.ws_thread.start()
                
                # Wait for connection
                timeout = 5
                start = time.time()
                while not self.connected and (time.time() - start) < timeout:
                    time.sleep(0.1)
                
                if self.connected:
                    logger.info(f"✅ Connected to {url}")
                    self.port = port
                    self.use_ssl = use_ssl
                    return True
                else:
                    logger.warning(f"⏱️ Connection timeout on {url}")
                    if self.ws:
                        self.ws.close()
                    time.sleep(1)
                    
            except Exception as e:
                logger.warning(f"❌ Failed on {port}: {e}")
                if self.ws:
                    try:
                        self.ws.close()
                    except:
                        pass
                time.sleep(1)
        
        logger.error("❌ Failed to connect to TV on any port")
        return False

    def _on_open(self, ws):
        """WebSocket connection opened"""
        logger.info("🔌 WebSocket connection established")
        self.connected = True
        self._authenticate()

    def _on_message(self, ws, message: str):
        """Handle incoming WebSocket message"""
        try:
            logger.debug(f"📨 Message received: {message[:200]}")
            
            # Try to parse as JSON
            try:
                data = json.loads(message)
                self._process_message(data)
            except json.JSONDecodeError:
                # Try to decrypt if it looks like base64/encrypted
                self._try_decrypt_message(message)
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")

    def _on_error(self, ws, error):
        """WebSocket error occurred"""
        logger.error(f"❌ WebSocket error: {error}")
        self.connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        logger.warning(f"🔴 Connection closed: {close_status_code} - {close_msg}")
        self.connected = False

    def _authenticate(self):
        """Perform handshake/authentication with TV"""
        try:
            # Initial handshake message
            handshake = {
                "action": "handshake",
                "type": "request"
            }
            self._send_command(handshake)
            logger.info("🔐 Handshake sent")
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")

    def _encrypt_payload(self, payload: str) -> Optional[str]:
        """Encrypt payload using AES-128-CBC"""
        try:
            cipher = AES.new(self.cipher_key, AES.MODE_CBC, self.cipher_iv)
            padded = pad(payload.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Encryption error: {e}")
            return None

    def _decrypt_payload(self, encrypted_payload: str) -> Optional[str]:
        """Decrypt payload using AES-128-CBC"""
        try:
            cipher = AES.new(self.cipher_key, AES.MODE_CBC, self.cipher_iv)
            decoded = base64.b64decode(encrypted_payload)
            decrypted = cipher.decrypt(decoded)
            unpadded = unpad(decrypted, AES.block_size)
            return unpadded.decode('utf-8')
        except Exception as e:
            logger.debug(f"Decryption failed (may not be encrypted): {e}")
            return None

    def _try_decrypt_message(self, message: str):
        """Attempt to decrypt encrypted message"""
        decrypted = self._decrypt_payload(message)
        if decrypted:
            try:
                data = json.loads(decrypted)
                self._process_message(data)
            except json.JSONDecodeError:
                logger.debug(f"Decrypted message is not JSON: {decrypted[:100]}")

    def _process_message(self, data: Dict[str, Any]):
        """Process received JSON message"""
        try:
            action = data.get('action', '').lower()
            msg_type = data.get('type', '').lower()
            
            logger.debug(f"📋 Processing action={action}, type={msg_type}")
            
            # Handshake response
            if action == 'handshake' and msg_type == 'response':
                logger.info("✅ Handshake successful")
                # Update encryption keys if provided
                if 'cipher' in data:
                    self._update_cipher(data['cipher'])
                self._request_state()
                
            # State update
            elif action == 'state' or 'power' in data:
                self._update_state(data)
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")

    def _update_state(self, data: Dict[str, Any]):
        """Update local state from received data"""
        if 'power' in data:
            self.state['power'] = 'ON' if data.get('power') else 'OFF'
        if 'volume' in data:
            self.state['volume'] = data.get('volume', 0)
        if 'mute' in data or 'muted' in data:
            self.state['muted'] = data.get('mute') or data.get('muted', False)
        if 'sourceid' in data or 'source' in data:
            self.state['source'] = data.get('sourceid') or data.get('source')
        if 'channel' in data:
            self.state['channel'] = data.get('channel')
        
        logger.debug(f"State updated: {self.state}")

    def _update_cipher(self, cipher_data: Dict[str, Any]):
        """Update encryption keys from TV response"""
        try:
            if 'key' in cipher_data:
                self.cipher_key = base64.b64decode(cipher_data['key'])
            if 'iv' in cipher_data:
                self.cipher_iv = base64.b64decode(cipher_data['iv'])
            logger.info("🔑 Encryption keys updated")
        except Exception as e:
            logger.warning(f"Failed to update cipher keys: {e}")

    def _request_state(self):
        """Request current state from TV"""
        command = {
            "action": "state",
            "type": "request"
        }
        self._send_command(command)

    def _send_command(self, command: Dict[str, Any]) -> bool:
        """Send command to TV"""
        if not self.connected or not self.ws:
            logger.warning("⚠️ TV not connected, cannot send command")
            return False
        
        try:
            message = json.dumps(command)
            logger.debug(f"📤 Sending command: {message}")
            self.ws.send(message)
            return True
        except Exception as e:
            logger.error(f"❌ Error sending command: {e}")
            return False

    def send_key(self, keycode: str) -> bool:
        """Send IR key to TV"""
        command = {
            "action": "sendkey",
            "type": "request",
            "keycode": keycode
        }
        return self._send_command(command)

    def power_on(self) -> bool:
        """Turn TV on"""
        return self.send_key("KEY_POWER")

    def power_off(self) -> bool:
        """Turn TV off"""
        return self.send_key("KEY_POWER")

    def volume_up(self) -> bool:
        """Increase volume"""
        return self.send_key("KEY_VOLUMEUP")

    def volume_down(self) -> bool:
        """Decrease volume"""
        return self.send_key("KEY_VOLUMEDOWN")

    def set_volume(self, level: int) -> bool:
        """Set volume to specific level (0-100)"""
        if not 0 <= level <= 100:
            logger.warning(f"⚠️ Volume level out of range: {level}")
            return False
        command = {
            "action": "setvolume",
            "type": "request",
            "volume": level
        }
        return self._send_command(command)

    def mute(self) -> bool:
        """Toggle mute"""
        return self.send_key("KEY_MUTE")

    def channel_up(self) -> bool:
        """Next channel"""
        return self.send_key("KEY_CHANNELUP")

    def channel_down(self) -> bool:
        """Previous channel"""
        return self.send_key("KEY_CHANNELDOWN")

    def set_channel(self, channel: int) -> bool:
        """Set channel to specific number"""
        if channel < 0:
            logger.warning(f"⚠️ Invalid channel number: {channel}")
            return False
        command = {
            "action": "setchannel",
            "type": "request",
            "channel": channel
        }
        return self._send_command(command)

    def set_source(self, source: str) -> bool:
        """Change input source"""
        source_map = {
            'HDMI1': 'KEY_HDMI1',
            'HDMI2': 'KEY_HDMI2',
            'HDMI3': 'KEY_HDMI3',
            'HDMI4': 'KEY_HDMI4',
            'TV': 'KEY_TV',
            'AV': 'KEY_AV',
            'DTMB': 'KEY_DTMB',
            'IPTV': 'KEY_IPTV'
        }
        
        key = source_map.get(source.upper())
        if key:
            return self.send_key(key)
        else:
            logger.warning(f"⚠️ Unknown source: {source}")
            return False

    def navigate(self, direction: str) -> bool:
        """Navigate menu"""
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
            logger.warning(f"⚠️ Unknown direction: {direction}")
            return False

    def disconnect(self):
        """Disconnect from TV"""
        self.connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        logger.info("✅ TV disconnected")


# ============================================================================
# MQTT BRIDGE CLASS
# ============================================================================

class MQTTBridge:
    """Manages MQTT to Hisense TV bridge"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mqtt_client: Optional[mqtt.Client] = None
        self.tv: Optional[HisenseTV] = None
        self.running = False
        
        # Calculate topic base
        self.base_topic = f"{config['mqtt_topic_prefix']}/{config['tv_name']}"
        self.command_topic = f"{self.base_topic}/command"
        self.state_topic = f"{self.base_topic}/state"
        self.availability_topic = f"{self.base_topic}/availability"

    def setup_mqtt(self) -> bool:
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client(
                client_id=f"hisense_tv_{self.config['tv_name']}"
            )
            
            if self.config['mqtt_user'] and self.config['mqtt_password']:
                self.mqtt_client.username_pw_set(
                    self.config['mqtt_user'],
                    self.config['mqtt_password']
                )
            
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            self.mqtt_client.will_set(
                self.availability_topic,
                payload="offline",
                qos=1,
                retain=True
            )
            
            logger.info(f"🌐 Connecting to MQTT broker: {self.config['mqtt_broker']}:{self.config['mqtt_port']}")
            self.mqtt_client.connect(
                self.config['mqtt_broker'],
                self.config['mqtt_port'],
                60
            )
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MQTT configuration error: {e}")
            return False

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker")
            
            client.publish(self.availability_topic, "online", qos=1, retain=True)
            client.subscribe(f"{self.command_topic}/#", qos=1)
            logger.info(f"📡 Subscribed to: {self.command_topic}/#")
            
            if self.config['auto_discovery']:
                self._publish_discovery()
        else:
            logger.error(f"❌ MQTT connection failed, code: {rc}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        if rc != 0:
            logger.warning(f"⚠️ Unexpected MQTT disconnection, code: {rc}")

    def _on_mqtt_message(self, client, userdata, msg):
        """MQTT message received callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"📨 MQTT message - Topic: {topic}, Payload: {payload}")
            
            command = topic.replace(f"{self.command_topic}/", "")
            self._process_command(command, payload)
            
        except Exception as e:
            logger.error(f"❌ MQTT message processing error: {e}")

    def _process_command(self, command: str, payload: str):
        """Process MQTT command"""
        if not self.tv or not self.tv.connected:
            logger.warning("⚠️ TV not connected, command ignored")
            return
        
        try:
            payload_lower = payload.lower()
            
            # Power commands
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
                        
            # Volume commands
            elif command == "volume":
                if payload_lower == "up":
                    self.tv.volume_up()
                elif payload_lower == "down":
                    self.tv.volume_down()
                elif payload.isdigit():
                    self.tv.set_volume(int(payload))
                    
            # Mute
            elif command == "mute":
                self.tv.mute()
                
            # Source
            elif command == "source":
                self.tv.set_source(payload)
                
            # Channel
            elif command == "channel":
                if payload_lower == "up":
                    self.tv.channel_up()
                elif payload_lower == "down":
                    self.tv.channel_down()
                elif payload.isdigit():
                    self.tv.set_channel(int(payload))
                    
            # Navigation
            elif command == "navigate":
                self.tv.navigate(payload)
                
            # Raw key
            elif command == "key":
                self.tv.send_key(payload)
                
            else:
                logger.warning(f"⚠️ Unknown command: {command}")
            
            # Publish state after command
            time.sleep(0.1)
            self._publish_state()
            
        except Exception as e:
            logger.error(f"❌ Command processing error: {e}")

    def _publish_state(self):
        """Publish TV state to MQTT"""
        if not self.tv or not self.mqtt_client:
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
            
            # Publish global state
            self.mqtt_client.publish(
                self.state_topic,
                json.dumps(state_data),
                qos=1,
                retain=True
            )
            
            # Publish individual states
            for key, value in state_data.items():
                if key != 'timestamp':
                    self.mqtt_client.publish(
                        f"{self.state_topic}/{key}",
                        str(value),
                        qos=1,
                        retain=True
                    )
            
            logger.debug(f"State published: {state_data}")
            
        except Exception as e:
            logger.error(f"❌ State publishing error: {e}")

    def _publish_discovery(self):
        """Publish Home Assistant discovery configuration"""
        logger.info("📢 Publishing Home Assistant auto-discovery")
        
        device_info = {
            "identifiers": [f"hisense_tv_{self.config['tv_name']}"],
            "name": f"Hisense TV {self.config['tv_name'].capitalize()}",
            "manufacturer": "Hisense",
            "model": "Vidaa U",
            "sw_version": "1.0.0"
        }
        
        # Media Player
        media_player_config = {
            "name": f"Hisense TV {self.config['tv_name'].capitalize()}",
            "unique_id": f"hisense_tv_{self.config['tv_name']}_media_player",
            "command_topic": f"{self.command_topic}/power",
            "state_topic": f"{self.state_topic}/power",
            "payload_on": "on",
            "payload_off": "off",
            "state_on": "ON",
            "state_off": "OFF",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:television"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/media_player/{self.config['tv_name']}/config",
            json.dumps(media_player_config),
            qos=1,
            retain=True
        )
        
        # Power switch
        switch_config = {
            "name": f"Hisense TV {self.config['tv_name'].capitalize()} Power",
            "unique_id": f"hisense_tv_{self.config['tv_name']}_power",
            "command_topic": f"{self.command_topic}/power",
            "state_topic": f"{self.state_topic}/power",
            "payload_on": "on",
            "payload_off": "off",
            "state_on": "ON",
            "state_off": "OFF",
            "availability_topic": self.availability_topic,
            "device": device_info,
            "icon": "mdi:power"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/switch/{self.config['tv_name']}_power/config",
            json.dumps(switch_config),
            qos=1,
            retain=True
        )
        
        # Volume sensor
        volume_sensor = {
            "name": f"Hisense TV {self.config['tv_name'].capitalize()} Volume",
            "unique_id": f"hisense_tv_{self.config['tv_name']}_volume",
            "state_topic": f"{self.state_topic}/volume",
            "availability_topic": self.availability_topic,
            "unit_of_measurement": "%",
            "device": device_info,
            "icon": "mdi:volume-high"
        }
        
        self.mqtt_client.publish(
            f"homeassistant/sensor/{self.config['tv_name']}_volume/config",
            json.dumps(volume_sensor),
            qos=1,
            retain=True
        )
        
        logger.info("✅ Discovery configuration published")

    def setup_tv(self) -> bool:
        """Initialize TV connection"""
        try:
            logger.info(f"📺 Initializing TV: {self.config['tv_ip']}:{self.config['tv_port']}")
            self.tv = HisenseTV(
                self.config['tv_ip'],
                self.config['tv_port'],
                self.config['tv_ssl']
            )
            
            tv_thread = Thread(target=self.tv.connect, daemon=True)
            tv_thread.start()
            
            timeout = 10
            start_time = time.time()
            while not self.tv.connected and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            if self.tv.connected:
                logger.info("✅ TV connected successfully")
                return True
            else:
                logger.warning("⏱️ TV connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ TV setup error: {e}")
            return False

    def state_monitor(self):
        """Monitor TV state and publish updates"""
        logger.info("📊 Starting state monitoring")
        
        while self.running:
            try:
                if self.tv and self.tv.connected:
                    self.tv._request_state()
                    time.sleep(1)
                    self._publish_state()
                else:
                    logger.warning("⚠️ TV disconnected, attempting reconnection...")
                    if self.mqtt_client:
                        self.mqtt_client.publish(
                            self.availability_topic,
                            "offline",
                            qos=1,
                            retain=True
                        )
                    
                    if self.setup_tv():
                        if self.mqtt_client:
                            self.mqtt_client.publish(
                                self.availability_topic,
                                "online",
                                qos=1,
                                retain=True
                            )
                
                time.sleep(self.config['scan_interval'])
                
            except Exception as e:
                logger.error(f"❌ State monitoring error: {e}")
                time.sleep(self.config['scan_interval'])

    def run(self) -> bool:
        """Start the bridge"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Hisense TV MQTT Bridge")
        logger.info("=" * 60)
        
        self.running = True
        
        # Setup MQTT
        if not self.setup_mqtt():
            logger.error("❌ MQTT setup failed")
            return False
        
        # Setup TV
        if not self.setup_tv():
            logger.error("❌ TV setup failed")
            return False
        
        # Start monitoring
        monitor_thread = Thread(target=self.state_monitor, daemon=True)
        monitor_thread.start()
        
        logger.info("✅ Bridge started successfully")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
            self.stop()
        
        return True

    def stop(self):
        """Shutdown the bridge"""
        logger.info("🛑 Stopping bridge...")
        
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.publish(
                self.availability_topic,
                "offline",
                qos=1,
                retain=True
            )
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.tv:
            self.tv.disconnect()
        
        logger.info("✅ Bridge stopped")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    try:
        bridge = MQTTBridge(CONFIG)
        bridge.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
