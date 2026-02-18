ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

# Variables de build
ARG BUILD_VERSION
ARG BUILD_ARCH

# Installation des dépendances système
RUN apk add --no-cache \
    python3 \
    py3-pip \
    openssl \
    mosquitto-clients \
    jq \
    tzdata

# Installation des dépendances Python
RUN pip3 install --no-cache-dir \
    paho-mqtt==1.6.1 \
    websocket-client==1.6.4 \
    requests==2.31.0 \
    asyncio==3.4.3 \
    pycryptodome==3.19.0

# Copie de la structure rootfs (contient /app/hisense_mqtt_bridge.py)
COPY rootfs /

# Permissions sur les scripts de service
RUN chmod a+x /etc/services.d/hisense-mqtt/run && \
    chmod a+x /etc/services.d/hisense-mqtt/finish

# Labels
LABEL \
    io.hass.name="Hisense TV MQTT Bridge" \
    io.hass.description="Bridge MQTT pour contrôler les TV Hisense" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

