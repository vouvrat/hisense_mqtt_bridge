ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.14-alpine3.24
FROM ${BUILD_FROM}

# Variables de build
ARG BUILD_VERSION
ARG BUILD_ARCH

# Installation des dépendances système
# (python3/pip déjà fournis par l'image de base ghcr.io/home-assistant/base-python,
# vérifié dans son Dockerfile source : ensurepip + symlinks python3/pip3 —
# mosquitto-clients et jq retirés, non utilisés par le code ni les scripts)
RUN apk add --no-cache \
    openssl \
    tzdata

# Installation des dépendances Python (source unique : requirements.txt)
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

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

