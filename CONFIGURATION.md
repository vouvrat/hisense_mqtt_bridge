# Configuration Guide

## Environment Variables

All configuration is done through environment variables:

### MQTT Configuration
- `MQTT_BROKER` (default: `localhost`) - MQTT broker hostname or IP
- `MQTT_PORT` (default: `1883`) - MQTT broker port
- `MQTT_USER` (default: `""`) - MQTT username (optional)
- `MQTT_PASSWORD` (default: `""`) - MQTT password (optional)
- `MQTT_TOPIC_PREFIX` (default: `hisense_tv`) - Base topic prefix for MQTT

### TV Configuration
- `TV_IP` (**REQUIRED**) - IP address of your Hisense VIDAA-U TV
- `TV_PORT` (default: `10001`) - WebSocket port on TV
  - `10001` - Standard VIDAA-U port (recommended)
  - `36669`, `36670`, `36870` - Legacy ports (auto-detected if primary fails)
- `TV_NAME` (default: `salon`) - Name of the TV (used in MQTT topics)
- `TV_SSL` (default: `false`) - Enable SSL/TLS for WebSocket connection

### Bridge Configuration
- `AUTO_DISCOVERY` (default: `true`) - Enable Home Assistant auto-discovery
- `SCAN_INTERVAL` (default: `30`) - State update interval in seconds
- `LOG_LEVEL` (default: `INFO`) - Logging level (DEBUG, INFO, WARNING, ERROR)

## Example Configuration

```bash
# Basic setup
export TV_IP="192.168.1.100"
export TV_NAME="living_room"
export MQTT_BROKER="192.168.1.10"
export MQTT_USER="mqtt_user"
export MQTT_PASSWORD="mqtt_pass"

# Advanced
export TV_PORT="10001"
export TV_SSL="false"
export AUTO_DISCOVERY="true"
export SCAN_INTERVAL="30"
export LOG_LEVEL="INFO"
```

## MQTT Topics

Topics follow the pattern: `{MQTT_TOPIC_PREFIX}/{TV_NAME}/...`

### State Topics (Read-Only)
- `hisense_tv/living_room/state` - Global state JSON
- `hisense_tv/living_room/state/power` - Power state (ON/OFF)
- `hisense_tv/living_room/state/volume` - Volume level (0-100)
- `hisense_tv/living_room/state/muted` - Mute state (True/False)
- `hisense_tv/living_room/state/source` - Current input source
- `hisense_tv/living_room/state/channel` - Current channel
- `hisense_tv/living_room/availability` - Bridge availability (online/offline)

### Command Topics (Write)
- `hisense_tv/living_room/command/power` - Power control
  - Payload: `on`, `off`, `toggle`
- `hisense_tv/living_room/command/volume` - Volume control
  - Payload: `up`, `down`, or numeric level (0-100)
- `hisense_tv/living_room/command/mute` - Toggle mute
  - Payload: (any value)
- `hisense_tv/living_room/command/channel` - Channel control
  - Payload: `up`, `down`, or numeric channel
- `hisense_tv/living_room/command/source` - Change input source
  - Payload: `HDMI1`, `HDMI2`, `HDMI3`, `HDMI4`, `TV`, `AV`, `DTMB`, `IPTV`
- `hisense_tv/living_room/command/navigate` - Menu navigation
  - Payload: `UP`, `DOWN`, `LEFT`, `RIGHT`, `OK`, `BACK`, `HOME`, `MENU`
- `hisense_tv/living_room/command/key` - Send raw IR key code
  - Payload: Key code (e.g., `KEY_POWER`, `KEY_VOLUMEUP`)

## MQTT Examples

### Turn on TV
```bash
mosquitto_pub -h 192.168.1.10 -t hisense_tv/living_room/command/power -m "on"
```

### Set volume to 50%
```bash
mosquitto_pub -h 192.168.1.10 -t hisense_tv/living_room/command/volume -m "50"
```

### Change to HDMI1
```bash
mosquitto_pub -h 192.168.1.10 -t hisense_tv/living_room/command/source -m "HDMI1"
```

### Get current state
```bash
mosquitto_sub -h 192.168.1.10 -t hisense_tv/living_room/state/#
```

## Home Assistant Integration

When `AUTO_DISCOVERY=true`, the bridge automatically publishes MQTT device configurations for:
- Media Player
- Power Switch
- Volume Sensor
- Mute Switch
- Source Sensor

These will appear automatically in Home Assistant under **Settings → Devices & Services → MQTT**.

## Troubleshooting

### Bridge won't connect to TV
1. Verify `TV_IP` is correct and TV is on the same network
2. Check if TV is listening on port 10001 with: `nmap -p 10001 <TV_IP>`
3. Enable DEBUG logging: `LOG_LEVEL=DEBUG`
4. See if connection works on alternate ports (36669, 36870)

### MQTT messages not received
1. Verify MQTT broker is accessible: `mosquitto_sub -h <broker> -t "#"`
2. Check `MQTT_USER` and `MQTT_PASSWORD` are correct
3. Verify firewall allows MQTT port (default 1883)

### State updates not appearing
1. Check `SCAN_INTERVAL` is reasonable (default 30 seconds)
2. Verify TV is responding to commands
3. Check logs for connection errors
