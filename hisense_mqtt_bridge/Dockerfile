ARG BUILD_FROM
FROM $BUILD_FROM

# Variables d'environnement
ENV LANG C.UTF-8

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

# Copie des fichiers
COPY rootfs /

# Permissions
RUN chmod a+x /etc/services.d/hisense-mqtt/run && \
    chmod a+x /etc/services.d/hisense-mqtt/finish && \
    chmod a+x /run.sh

WORKDIR /app

# Script principal Python
COPY hisense_mqtt_bridge.py /app/

CMD [ "/run.sh" ]
