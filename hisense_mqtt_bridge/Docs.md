# Documentation Hisense TV MQTT Bridge

## Configuration

### Paramètres obligatoires

- **tv_ip**: Adresse IP de votre TV Hisense
- **mqtt_broker**: Adresse du broker MQTT (par défaut: core-mosquitto)

### Paramètres optionnels

- **mqtt_port**: Port MQTT (défaut: 1883)
- **mqtt_user**: Utilisateur MQTT (si authentification)
- **mqtt_password**: Mot de passe MQTT
- **mqtt_topic_prefix**: Préfixe des topics (défaut: hisense_tv)
- **tv_name**: Nom de la TV (défaut: salon)
- **ssl_enabled**: Utiliser SSL pour la TV (défaut: true)
- **auto_discovery**: Activer l'auto-discovery HA (défaut: true)
- **scan_interval**: Intervalle de mise à jour en secondes (défaut: 30)
- **log_level**: Niveau de log (debug, info, warning, error)

## Exemple de configuration

```yaml
mqtt_broker: "192.168.1.100"
mqtt_port: 1883
mqtt_user: "homeassistant"
mqtt_password: "votre_mot_de_passe"
mqtt_topic_prefix: "hisense_tv"
tv_ip: "192.168.1.50"
tv_name: "salon"
ssl_enabled: true
auto_discovery: true
scan_interval: 30
log_level: "info"
