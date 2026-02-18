ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18
FROM ${BUILD_FROM}

# Variables d'environnement
ENV LANG=C.UTF-8

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

# Copie des fichiers rootfs
COPY rootfs /

# Permissions pour les scripts de service
RUN chmod a+x /etc/services.d/hisense-mqtt/run && \
    chmod a+x /etc/services.d/hisense-mqtt/finish

# Copie du script Python principal
RUN mkdir -p /app
COPY hisense_mqtt_bridge.py /app/

# Labels
LABEL \
    io.hass.name="Hisense TV MQTT Bridge" \
    io.hass.description="Bridge MQTT pour contrôler les TV Hisense" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD pgrep -f hisense_mqtt_bridge.py || exit 1
