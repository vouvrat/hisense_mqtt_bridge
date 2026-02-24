#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Démarrage de Hisense TV MQTT Bridge..."

# Récupération de la configuration
CONFIG_PATH=/data/options.json

export MQTT_BROKER=$(bashio::config 'mqtt_broker')
export MQTT_PORT=$(bashio::config 'mqtt_port')
export MQTT_USER=$(bashio::config 'mqtt_user')
export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
export MQTT_TOPIC_PREFIX=$(bashio::config 'mqtt_topic_prefix')
export TV_IP=$(bashio::config 'tv_ip')
export TV_PORT=$(bashio::config 'tv_port')
export TV_NAME=$(bashio::config 'tv_name')
export TV_SSL=$(bashio::config 'tv_ssl')
export AUTO_DISCOVERY=$(bashio::config 'auto_discovery')
export SCAN_INTERVAL=$(bashio::config 'scan_interval')
export LOG_LEVEL=$(bashio::config 'log_level')

# Validation des paramètres obligatoires
if bashio::var.is_empty "${TV_IP}"; then
    bashio::log.fatal "L'adresse IP de la TV est obligatoire!"
    exit 1
fi

if bashio::var.is_empty "${MQTT_BROKER}"; then
    bashio::log.fatal "L'adresse du broker MQTT est obligatoire!"
    exit 1
fi

bashio::log.info "Configuration:"
bashio::log.info "- Broker MQTT: ${MQTT_BROKER}:${MQTT_PORT}"
bashio::log.info "- TV IP: ${TV_IP}:${TV_PORT}"
bashio::log.info "- TV Name: ${TV_NAME}"
bashio::log.info "- TV SSL: ${TV_SSL}"
bashio::log.info "- Topic prefix: ${MQTT_TOPIC_PREFIX}"
bashio::log.info "- Auto-discovery: ${AUTO_DISCOVERY}"

# Lancement du script Python
bashio::log.info "Démarrage du bridge..."
exec python3 /app/hisense_mqtt_bridge.py
