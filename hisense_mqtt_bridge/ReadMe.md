# Hisense TV MQTT Bridge pour Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

_Addon Home Assistant pour contrôler votre TV Hisense Vidaa via MQTT_

**Cet addon crée un pont entre votre TV Hisense et votre broker MQTT, permettant un contrôle complet via Home Assistant.**

![Logo Hisense MQTT Bridge](logo.png)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Pré-requis](#-pré-requis)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Utilisation](#-utilisation)
- [Intégration Home Assistant](#-intégration-home-assistant)
- [Dépannage](#-dépannage)
- [Contributions](#-contributions)
- [Support](#-support)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### Contrôles disponibles

- ✅ **Alimentation** : Allumer/Éteindre la TV
- ✅ **Volume** : Augmenter/Diminuer/Muet
- ✅ **Sources** : Changer entre HDMI1-4, TV, AV
- ✅ **Chaînes** : Navigation chaînes suivante/précédente
- ✅ **Navigation** : Contrôle directionnel complet (Haut/Bas/Gauche/Droite/OK)
- ✅ **Touches** : Envoi de n'importe quelle touche de télécommande
- ✅ **État en temps réel** : Surveillance continue de l'état de la TV

### Intégrations

- 🏠 **Auto-discovery Home Assistant** : Configuration automatique des entités
- 📡 **MQTT** : Communication bidirectionnelle via votre broker existant
- 🔄 **Reconnexion automatique** : Gestion intelligente des déconnexions
- 🔐 **SSL/TLS** : Support de la connexion sécurisée
- 📊 **Logging détaillé** : Plusieurs niveaux de verbosité

---

## 🔧 Pré-requis

### Hardware

- 📺 **TV Hisense** avec système **Vidaa** (Vidaa U3, U4, U5, U6)
- 🏠 **Home Assistant** (version 2023.1 ou supérieure recommandée)
- 🌐 **Réseau local** : TV et Home Assistant sur le même réseau

### Software

- 🦟 **Broker MQTT** installé et fonctionnel :
  - [Mosquitto broker](https://github.com/home-assistant/addons/tree/master/mosquitto) (recommandé)
  - Ou n'importe quel broker MQTT compatible
  
- 🔌 **Intégration MQTT** configurée dans Home Assistant

> ⚠️ **Important** : Assurez-vous que votre intégration MQTT fonctionne avant d'installer cet addon.

---

## 📥 Installation

### Méthode 1 : Installation via HACS (Recommandée)

[![Ouvrir votre instance Home Assistant et ouvrir un dépôt dans le magasin communautaire Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=VOTRE_USERNAME&repository=hisense-mqtt-bridge&category=addon)

1. **Assurez-vous d'avoir [HACS](https://hacs.xyz/) installé**

2. **Ajoutez ce repository à HACS** :
   - Cliquez sur **HACS** dans la barre latérale
   - Cliquez sur **Intégrations**
   - Cliquez sur les **3 points** en haut à droite
   - Sélectionnez **Dépôts personnalisés**
   - Collez l'URL : `https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge`
   - Catégorie : **Addon**
   - Cliquez sur **Ajouter**

3. **Installez l'addon** :
   - Recherchez "Hisense TV MQTT Bridge"
   - Cliquez sur **Télécharger**
   - Redémarrez Home Assistant si demandé

### Méthode 2 : Installation manuelle

1. **Ajoutez le repository** :
   - Allez dans **Paramètres** → **Modules complémentaires** → **Boutique des modules complémentaires**
   - Cliquez sur les **⋮** (3 points verticaux) en haut à droite
   - Sélectionnez **Dépôts**
   - Ajoutez cette URL : `https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge`
   - Cliquez sur **Ajouter**

2. **Installez l'addon** :
   - Actualisez la page (F5)
   - Recherchez "Hisense TV MQTT Bridge"
   - Cliquez sur l'addon
   - Cliquez sur **Installer**
   - Patientez pendant l'installation (peut prendre quelques minutes)

### Méthode 3 : Installation depuis le dépôt Git (Développeurs)

```bash
cd /addons
git clone https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge.git
cd hisense-mqtt-bridge
```

Puis rechargez les addons dans Home Assistant.

---

## ⚙️ Configuration

### Configuration minimale

```yaml
tv_ip: "192.168.1.50"              # IP de votre TV Hisense
mqtt_broker: "core-mosquitto"       # Adresse de votre broker MQTT
tv_name: "salon"                    # Nom de votre TV
```

### Configuration complète

```yaml
# Configuration MQTT (Obligatoire)
mqtt_broker: "192.168.1.100"        # IP ou hostname du broker
mqtt_port: 1883                     # Port MQTT (défaut: 1883)
mqtt_user: "homeassistant"          # Utilisateur MQTT (optionnel)
mqtt_password: "votre_password"     # Mot de passe MQTT (optionnel)
mqtt_topic_prefix: "hisense_tv"     # Préfixe des topics (défaut: hisense_tv)

# Configuration TV (Obligatoire)
tv_ip: "192.168.1.50"               # IP de votre TV Hisense
tv_name: "salon"                    # Nom unique pour cette TV

# Options avancées (Optionnel)
ssl_enabled: true                   # Utiliser SSL pour la connexion TV (défaut: true)
auto_discovery: true                # Auto-discovery Home Assistant (défaut: true)
scan_interval: 30                   # Intervalle de mise à jour en secondes (défaut: 30)
log_level: "info"                   # Niveau de log: debug|info|warning|error
```

### 📝 Description des paramètres

| Paramètre | Type | Requis | Défaut | Description |
|-----------|------|--------|--------|-------------|
| `mqtt_broker` | string | ✅ | - | Adresse IP ou hostname du broker MQTT |
| `mqtt_port` | int | ❌ | 1883 | Port du broker MQTT |
| `mqtt_user` | string | ❌ | "" | Nom d'utilisateur MQTT (si authentification activée) |
| `mqtt_password` | string | ❌ | "" | Mot de passe MQTT (si authentification activée) |
| `mqtt_topic_prefix` | string | ❌ | "hisense_tv" | Préfixe pour tous les topics MQTT |
| `tv_ip` | string | ✅ | - | Adresse IP de votre TV Hisense |
| `tv_name` | string | ❌ | "salon" | Nom unique pour identifier cette TV |
| `ssl_enabled` | bool | ❌ | true | Active la connexion SSL/TLS vers la TV |
| `auto_discovery` | bool | ❌ | true | Active l'auto-discovery Home Assistant |
| `scan_interval` | int | ❌ | 30 | Intervalle de mise à jour de l'état (10-300s) |
| `log_level` | string | ❌ | "info" | Niveau de détail des logs |

### 🔍 Trouver l'IP de votre TV

#### Méthode 1 : Depuis la TV
1. Appuyez sur **Paramètres** sur votre télécommande
2. Allez dans **Réseau** → **Configuration réseau**
3. Sélectionnez votre connexion (WiFi ou Ethernet)
4. Notez l'**adresse IP**

#### Méthode 2 : Depuis votre routeur
1. Connectez-vous à l'interface web de votre routeur
2. Cherchez la liste des appareils connectés
3. Recherchez un appareil nommé "Hisense" ou "TV"

#### Méthode 3 : Scan réseau
```bash
# Linux/Mac
nmap -sn 192.168.1.0/24 | grep -i hisense

# Ou avec arp
arp -a | grep -i hisense
```

### ⚙️ Procédure de configuration pas à pas

1. **Ouvrez l'addon** dans Home Assistant
   - Allez dans **Paramètres** → **Modules complémentaires**
   - Cliquez sur **Hisense TV MQTT Bridge**

2. **Configurez l'addon** :
   - Cliquez sur l'onglet **Configuration**
   - Remplissez au minimum `tv_ip` et `mqtt_broker`
   - Sauvegardez avec le bouton **Enregistrer**

3. **Options de démarrage** :
   - ✅ Activez **Démarrer au démarrage** pour un lancement automatique
   - ✅ Activez **Chien de garde** pour une surveillance automatique
   - ℹ️ Laissez **Afficher dans la barre latérale** désactivé (pas d'interface web)

4. **Démarrez l'addon** :
   - Cliquez sur l'onglet **Journal**
   - Cliquez sur **Démarrer**
   - Surveillez les logs pour vérifier la connexion

5. **Vérification** :
   ```
   ✅ Connexion au broker MQTT réussie
   ✅ Connexion WebSocket établie
   ✅ Handshake réussi
   ✅ Configuration auto-discovery publiée
   ✅ Bridge démarré avec succès
   ```

---

## 🎮 Utilisation

### Topics MQTT

L'addon crée automatiquement une structure de topics MQTT :

#### 📤 Topics de commande (Publier vers)

```
hisense_tv/{tv_name}/command/power        → on | off | toggle
hisense_tv/{tv_name}/command/volume       → up | down | 0-100
hisense_tv/{tv_name}/command/mute         → toggle
hisense_tv/{tv_name}/command/channel      → up | down | numéro
hisense_tv/{tv_name}/command/source       → HDMI1 | HDMI2 | HDMI3 | HDMI4 | TV | AV
hisense_tv/{tv_name}/command/navigate     → UP | DOWN | LEFT | RIGHT | OK | BACK | HOME | MENU
hisense_tv/{tv_name}/command/key          → CODE_TOUCHE (voir liste ci-dessous)
```

#### 📥 Topics d'état (S'abonner à)

```
hisense_tv/{tv_name}/state                → État complet (JSON)
hisense_tv/{tv_name}/state/power          → ON | OFF
hisense_tv/{tv_name}/state/volume         → 0-100
hisense_tv/{tv_name}/state/muted          → true | false
hisense_tv/{tv_name}/state/source         → Source actuelle
hisense_tv/{tv_name}/state/channel        → Chaîne actuelle
hisense_tv/{tv_name}/availability         → online | offline
```

### 🎹 Codes des touches

#### Contrôles de base
```
KEY_POWER                → Marche/Arrêt
KEY_VOLUMEUP            → Volume +
KEY_VOLUMEDOWN          → Volume -
KEY_MUTE                → Muet
KEY_CHANNELUP           → Chaîne +
KEY_CHANNELDOWN         → Chaîne -
```

#### Navigation
```
KEY_UP                  → Haut
KEY_DOWN                → Bas
KEY_LEFT                → Gauche
KEY_RIGHT               → Droite
KEY_OK / KEY_ENTER      → Valider
KEY_BACK / KEY_RETURN   → Retour
KEY_HOME                → Accueil
KEY_MENU                → Menu
KEY_EXIT                → Sortie
```

#### Sources
```
KEY_HDMI1               → HDMI 1
KEY_HDMI2               → HDMI 2
KEY_HDMI3               → HDMI 3
KEY_HDMI4               → HDMI 4
KEY_TV                  → TV
KEY_AV                  → AV
```

#### Lecture multimédia
```
KEY_PLAY                → Lecture
KEY_PAUSE               → Pause
KEY_STOP                → Stop
KEY_REWIND              → Retour rapide
KEY_FASTFORWARD         → Avance rapide
KEY_RECORD              → Enregistrer
```

#### Chiffres
```
KEY_0 à KEY_9           → Chiffres 0-9
```

#### Applications (si disponibles)
```
KEY_NETFLIX             → Netflix
KEY_YOUTUBE             → YouTube
KEY_AMAZON              → Amazon Prime
KEY_APPS                → Menu des applications
```

### 📝 Exemples de commandes MQTT

#### Avec mosquitto_pub (ligne de commande)

```bash
# Allumer la TV
mosquitto_pub -h localhost -t "hisense_tv/salon/command/power" -m "on"

# Volume à 50
mosquitto_pub -h localhost -t "hisense_tv/salon/command/volume" -m "50"

# Changer vers HDMI1
mosquitto_pub -h localhost -t "hisense_tv/salon/command/source" -m "HDMI1"

# Navigation
mosquitto_pub -h localhost -t "hisense_tv/salon/command/navigate" -m "UP"

# Touche spécifique
mosquitto_pub -h localhost -t "hisense_tv/salon/command/key" -m "KEY_NETFLIX"
```

#### Avec MQTT Explorer

1. Connectez-vous à votre broker
2. Naviguez vers `hisense_tv/salon/command/`
3. Cliquez sur un topic
4. Envoyez votre commande dans le champ "Publish"

---

## 🏠 Intégration Home Assistant

### Auto-discovery

Si `auto_discovery` est activé (par défaut), les entités suivantes sont créées automatiquement :

#### Entités créées

| Entité | Type | Description |
|--------|------|-------------|
| `media_player.hisense_tv_salon` | Media Player | Contrôle principal de la TV |
| `switch.hisense_tv_salon_power` | Switch | Interrupteur marche/arrêt |
| `sensor.hisense_tv_salon_volume` | Sensor | Volume actuel (0-100%) |
| `switch.hisense_tv_salon_mute` | Switch | Muet on/off |
| `sensor.hisense_tv_salon_source` | Sensor | Source actuelle |

### 🤖 Automatisations

#### Exemple 1 : Allumer la TV le matin

```yaml
automation:
  - alias: "TV Salon - Allumer le matin"
    description: "Allume automatiquement la TV à 7h du lundi au vendredi"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
    action:
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/power"
          payload: "on"
      - delay: "00:00:05"
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/source"
          payload: "TV"
```

#### Exemple 2 : Éteindre la TV la nuit

```yaml
automation:
  - alias: "TV Salon - Extinction automatique"
    description: "Éteint la TV à minuit si elle est allumée"
    trigger:
      - platform: time
        at: "00:00:00"
    condition:
      - condition: state
        entity_id: media_player.hisense_tv_salon
        state: "on"
    action:
      - service: notify.mobile_app_iphone
        data:
          message: "La TV va s'éteindre dans 5 minutes"
      - delay: "00:05:00"
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/power"
          payload: "off"
```

#### Exemple 3 : Volume adaptatif selon l'heure

```yaml
automation:
  - alias: "TV Salon - Volume adaptatif"
    description: "Ajuste le volume selon l'heure de la journée"
    trigger:
      - platform: state
        entity_id: media_player.hisense_tv_salon
        to: "on"
    action:
      - choose:
          # Matin (6h-9h) : Volume modéré
          - conditions:
              - condition: time
                after: "06:00:00"
                before: "09:00:00"
            sequence:
              - service: mqtt.publish
                data:
                  topic: "hisense_tv/salon/command/volume"
                  payload: "20"
          
          # Journée (9h-22h) : Volume normal
          - conditions:
              - condition: time
                after: "09:00:00"
                before: "22:00:00"
            sequence:
              - service: mqtt.publish
                data:
                  topic: "hisense_tv/salon/command/volume"
                  payload: "35"
          
          # Nuit (22h-6h) : Volume faible
          - conditions:
              - condition: time
                after: "22:00:00"
            sequence:
              - service: mqtt.publish
                data:
                  topic: "hisense_tv/salon/command/volume"
                  payload: "15"
```

### 📜 Scripts

#### Script 1 : Lancer Netflix

```yaml
script:
  tv_salon_netflix:
    alias: "TV Salon - Lancer Netflix"
    icon: mdi:netflix
    sequence:
      # Allumer la TV
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/power"
          payload: "on"
      
      # Attendre que la TV démarre
      - delay: "00:00:03"
      
      # Lancer Netflix
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/key"
          payload: "KEY_NETFLIX"
```

#### Script 2 : Mode cinéma

```yaml
script:
  tv_salon_mode_cinema:
    alias: "TV Salon - Mode Cinéma"
    icon: mdi:movie-open
    sequence:
      # Allumer la TV
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/power"
          payload: "on"
      
      # Changer vers HDMI1 (lecteur Blu-ray)
      - delay: "00:00:02"
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/source"
          payload: "HDMI1"
      
      # Ajuster le volume
      - delay: "00:00:01"
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/volume"
          payload: "40"
      
      # Éteindre les lumières
      - service: light.turn_off
        target:
          entity_id: light.salon
```

#### Script 3 : Routine du soir

```yaml
script:
  tv_salon_routine_soir:
    alias: "TV Salon - Routine du soir"
    icon: mdi:weather-night
    sequence:
      # Allumer la TV
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/power"
          payload: "on"
      
      # Volume faible
      - delay: "00:00:02"
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/volume"
          payload: "15"
      
      # Chaîne info
      - service: mqtt.publish
        data:
          topic: "hisense_tv/salon/command/channel"
          payload: "27"
      
      # Lampe tamisée
      - service: light.turn_on
        target:
          entity_id: light.lampe_salon
        data:
          brightness: 50
```

### 🎨 Cartes Lovelace

#### Carte de contrôle basique

```yaml
type: entities
title: TV Salon
entities:
  - entity: media_player.hisense_tv_salon
    name: TV
  - entity: sensor.hisense_tv_salon_volume
    name: Volume
  - entity: sensor.hisense_tv_salon_source
    name: Source
  - type: buttons
    entities:
      - entity: script.tv_salon_netflix
        name: Netflix
        icon: mdi:netflix
      - entity: script.tv_salon_mode_cinema
        name: Cinéma
        icon: mdi:movie-open
```

#### Carte de télécommande complète

```yaml
type: vertical-stack
cards:
  # Titre
  - type: markdown
    content: |
      ## 📺 TV Salon
  
  # Contrôle Power
  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.hisense_tv_salon_power
        name: Power
        icon: mdi:power
        tap_action:
          action: toggle
      - type: button
        entity: switch.hisense_tv_salon_mute
        name: Mute
        icon: mdi:volume-mute
        tap_action:
          action: toggle
  
  # Volume
  - type: horizontal-stack
    cards:
      - type: button
        name: Vol -
        icon: mdi:volume-minus
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/volume
            payload: down
      - type: entity
        entity: sensor.hisense_tv_salon_volume
        name: Volume
      - type: button
        name: Vol +
        icon: mdi:volume-plus
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/volume
            payload: up
  
  # Navigation
  - type: vertical-stack
    cards:
      - type: horizontal-stack
        cards:
          - type: button
            icon: mdi:blank
            tap_action:
              action: none
          - type: button
            name: ⬆️
            tap_action:
              action: call-service
              service: mqtt.publish
              service_data:
                topic: hisense_tv/salon/command/navigate
                payload: UP
          - type: button
            icon: mdi:blank
            tap_action:
              action: none
      
      - type: horizontal-stack
        cards:
          - type: button
            name: ⬅️
            tap_action:
              action: call-service
              service: mqtt.publish
              service_data:
                topic: hisense_tv/salon/command/navigate
                payload: LEFT
          - type: button
            name: OK
            tap_action:
              action: call-service
              service: mqtt.publish
              service_data:
                topic: hisense_tv/salon/command/navigate
                payload: OK
          - type: button
            name: ➡️
            tap_action:
              action: call-service
              service: mqtt.publish
              service_data:
                topic: hisense_tv/salon/command/navigate
                payload: RIGHT
      
      - type: horizontal-stack
        cards:
          - type: button
            icon: mdi:blank
            tap_action:
              action: none
          - type: button
            name: ⬇️
            tap_action:
              action: call-service
              service: mqtt.publish
              service_data:
                topic: hisense_tv/salon/command/navigate
                payload: DOWN
          - type: button
            icon: mdi:blank
            tap_action:
              action: none
  
  # Menu et retour
  - type: horizontal-stack
    cards:
      - type: button
        name: Back
        icon: mdi:arrow-left
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/navigate
            payload: BACK
      - type: button
        name: Home
        icon: mdi:home
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/navigate
            payload: HOME
      - type: button
        name: Menu
        icon: mdi:menu
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/navigate
            payload: MENU
  
  # Sources
  - type: horizontal-stack
    cards:
      - type: button
        name: HDMI1
        icon: mdi:hdmi-port
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/source
            payload: HDMI1
      - type: button
        name: HDMI2
        icon: mdi:hdmi-port
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/source
            payload: HDMI2
      - type: button
        name: TV
        icon: mdi:television-classic
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/source
            payload: TV
  
  # Applications
  - type: horizontal-stack
    cards:
      - type: button
        name: Netflix
        icon: mdi:netflix
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/key
            payload: KEY_NETFLIX
      - type: button
        name: YouTube
        icon: mdi:youtube
        tap_action:
          action: call-service
          service: mqtt.publish
          service_data:
            topic: hisense_tv/salon/command/key
            payload: KEY_YOUTUBE
```

### 🔔 Notifications

#### Notification de changement d'état

```yaml
automation:
  - alias: "TV Salon - Notification changement"
    trigger:
      - platform: mqtt
        topic: "hisense_tv/salon/state/power"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "TV Salon"
          message: >
            La TV est maintenant {{ trigger.payload }}
          data:
            push:
              sound: default
```

#### Alerte volume élevé

```yaml
automation:
  - alias: "TV Salon - Alerte volume"
    trigger:
      - platform: mqtt
        topic: "hisense_tv/salon/state/volume"
    condition:
      - condition: template
        value_template: "{{ trigger.payload | int > 70 }}"
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⚠️ Volume TV élevé"
          message: "Le volume de la TV est à {{ trigger.payload }}%"
```

---

## 🔧 Dépannage

### Problèmes courants

#### ❌ La TV ne se connecte pas

**Symptômes** :
- Logs : "Timeout connexion TV"
- Logs : "Erreur de connexion: [Errno 111] Connection refused"

**Solutions** :

1. **Vérifier l'IP de la TV** :
   ```bash
   ping 192.168.1.50
   ```

2. **Tester la connexion WebSocket** :
   ```bash
   telnet 192.168.1.50 36669
   ```

3. **Désactiver SSL** :
   ```yaml
   ssl_enabled: false
   ```

4. **Vérifier le pare-feu de la TV** :
   - Paramètres → Réseau → Pare-feu → Désactiver temporairement

5. **Redémarrer la TV** :
   - Débrancher 30 secondes puis rebrancher

#### ❌ Commandes MQTT non reçues

**Symptômes** :
- Les commandes ne s'exécutent pas
- Logs : "TV non connectée, commande ignorée"

**Solutions** :

1. **Vérifier la connexion MQTT** :
   ```bash
   mosquitto_sub -h localhost -t "hisense_tv/#" -v
   ```

2. **Tester une commande manuelle** :
   ```bash
   mosquitto_pub -h localhost -t "hisense_tv/salon/command/power" -m "on"
   ```

3. **Vérifier les credentials MQTT** :
   - Utilisateur et mot de passe corrects
   - Permissions de publication/souscription

4. **Vérifier les topics** :
   - Le nom de la TV correspond (`tv_name`)
   - Le préfixe est correct (`mqtt_topic_prefix`)

#### ❌ Pas d'auto-discovery

**Symptômes** :
- Les entités n'apparaissent pas dans Home Assistant
- Aucun appareil "Hisense TV" dans les intégrations

**Solutions** :

1. **Vérifier que auto-discovery est activé** :
   ```yaml
   auto_discovery: true
   ```

2. **Vérifier l'intégration MQTT** :
   - Paramètres → Appareils et services → MQTT
   - Vérifier que l'intégration est active

3. **Vérifier les topics de discovery** :
   ```bash
   mosquitto_sub -h localhost -t "homeassistant/#" -v
   ```

4. **Forcer la redécouverte** :
   - Redémarrer l'addon
   - Redémarrer Home Assistant
   - Supprimer et réinstaller l'addon

5. **Vérifier les logs MQTT** :
   - Paramètres → Système → Logs
   - Filtrer "mqtt"

#### ❌ Addon ne démarre pas

**Symptômes** :
- Logs : "TV_IP non défini!"
- Logs : "Échec configuration MQTT"
- Addon se coupe immédiatement

**Solutions** :

1. **Vérifier la configuration** :
   - `tv_ip` est renseigné
   - `mqtt_broker` est renseigné
   - Format JSON valide

2. **Vérifier les logs complets** :
   - Onglet Journal de l'addon
   - Rechercher les erreurs en rouge

3. **Réinstaller l'addon** :
   - Désinstaller
   - Redémarrer Home Assistant
   - Réinstaller

4. **Vérifier les dépendances** :
   - Broker MQTT installé et démarré
   - Intégration MQTT configurée

#### ❌ Déconnexions fréquentes

**Symptômes** :
- Logs : "Connexion fermée"
- Availability passe à "offline" régulièrement

**Solutions** :

1. **Augmenter scan_interval** :
   ```yaml
   scan_interval: 60  # Au lieu de 30
   ```

2. **Vérifier la stabilité réseau** :
   ```bash
   ping -c 100 192.168.1.50
   ```

3. **Désactiver le mode économie d'énergie** de la TV

4. **Utiliser une connexion Ethernet** au lieu du WiFi

5. **Vérifier les logs du broker MQTT** :
   - Rechercher des erreurs de timeout

### 🐛 Activer les logs détaillés

Pour obtenir plus d'informations de débogage :

```yaml
log_level: "debug"
```

Puis redémarrer l'addon et consulter les logs.

### 📊 Vérifier l'état MQTT

#### Surveiller tous les messages

```bash
mosquitto_sub -h localhost -u votre_user -P votre_password -t "hisense_tv/#" -v
```

#### Surveiller uniquement l'état

```bash
mosquitto_sub -h localhost -u votre_user -P votre_password -t "hisense_tv/salon/state/#" -v
```

#### Surveiller la disponibilité

```bash
mosquitto_sub -h localhost -u votre_user -P votre_password -t "hisense_tv/salon/availability" -v
```

### 🔍 Outils de diagnostic

#### Test de connexion TV

```python
import socket

def test_tv_connection(ip, port=36669):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"✅ Port {port} ouvert sur {ip}")
        else:
            print(f"❌ Port {port} fermé sur {ip}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        sock.close()

test_tv_connection("192.168.1.50")
```

#### Test MQTT

```bash
# Test de publication
mosquitto_pub -h localhost -t "test" -m "hello"

# Test de souscription
mosquitto_sub -h localhost -t "test" -v
```

### 📞 Obtenir de l'aide

Si le problème persiste :

1. **Activez les logs debug**
2. **Collectez les informations** :
   - Version de Home Assistant
   - Version de l'addon
   - Modèle exact de la TV
   - Version Vidaa
   - Logs de l'addon
   - Configuration (sans mots de passe)

3. **Ouvrez une issue** sur GitHub avec ces informations

---

## 🤝 Contributions

Les contributions sont les bienvenues ! 

### Comment contribuer

1. **Fork** le projet
2. **Créez une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-super-fonctionnalite
   ```
3. **Committez** vos changements :
   ```bash
   git commit -m "Ajout d'une super fonctionnalité"
   ```
4. **Poussez** vers la branche :
   ```bash
   git push origin feature/ma-super-fonctionnalite
   ```
5. **Ouvrez une Pull Request**

### Guidelines

- ✅ Code propre et commenté
- ✅ Respect de la structure existante
- ✅ Tests effectués sur une vraie TV
- ✅ Documentation mise à jour
- ✅ Changelog mis à jour

### Développement local

```bash
# Cloner le repo
git clone https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge.git
cd hisense-mqtt-bridge

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
python -m pytest tests/

# Lancer le bridge localement
export TV_IP=192.168.1.50
export MQTT_BROKER=localhost
python hisense_mqtt_bridge.py
```

---

## 💬 Support

### Documentation

- 📖 [Documentation complète](DOCS.md)
- 📝 [Changelog](CHANGELOG.md)
- 🐛 [Issues GitHub](https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge/issues)

### Communauté

- 💬 [Forum Home Assistant](https://community.home-assistant.io/)
- 💬 [Discord Home Assistant](https://discord.gg/home-assistant)
- 💬 [Reddit r/homeassistant](https://www.reddit.com/r/homeassistant/)

### Contact

- 📧 Email : votre.email@example.com
- 🐦 Twitter : [@votre_handle](https://twitter.com/votre_handle)
- 💼 LinkedIn : [Votre Profil](https://linkedin.com/in/votre-profil)

---

## 📜 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

```
MIT License

Copyright (c) 2024 Votre Nom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Remerciements

Merci à tous les contributeurs et à la communauté Home Assistant !

Projets et ressources qui ont inspiré ce travail :

- [sehaas/ha_hisense_tv](https://github.com/sehaas/ha_hisense_tv)
- [Krazy998/mqtt-hisensetv](https://github.com/Krazy998/mqtt-hisensetv)
- [d3nd3/Hisense-mqtt-keyfiles](https://github.com/d3nd3/Hisense-mqtt-keyfiles)
- [newAM/hisensetv_hass](https://github.com/newAM/hisensetv_hass)
- [Community Home Assistant](https://community.home-assistant.io/)

---

## ⭐ Statistiques

![GitHub stars](https://img.shields.io/github/stars/VOTRE_USERNAME/hisense-mqtt-bridge?style=social)
![GitHub forks](https://img.shields.io/github/forks/VOTRE_USERNAME/hisense-mqtt-bridge?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/VOTRE_USERNAME/hisense-mqtt-bridge?style=social)

![GitHub issues](https://img.shields.io/github/issues/VOTRE_USERNAME/hisense-mqtt-bridge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/VOTRE_USERNAME/hisense-mqtt-bridge)
![GitHub last commit](https://img.shields.io/github/last-commit/VOTRE_USERNAME/hisense-mqtt-bridge)

---

## 📸 Captures d'écran

### Interface Home Assistant

![Home Assistant Integration](screenshots/ha-integration.png)

### Carte Lovelace

![Lovelace Card](screenshots/lovelace-card.png)

### MQTT Explorer

![MQTT Topics](screenshots/mqtt-explorer.png)

---

<p align="center">
  Fait avec ❤️ pour la communauté Home Assistant
</p>

<p align="center">
  <a href="#-table-des-matières">Retour en haut ⬆️</a>
</p>

---

<!-- Liens des badges -->
[releases-shield]: https://img.shields.io/github/v/release/VOTRE_USERNAME/hisense-mqtt-bridge?style=for-the-badge
[releases]: https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/VOTRE_USERNAME/hisense-mqtt-bridge?style=for-the-badge
[commits]: https://github.com/VOTRE_USERNAME/hisense-mqtt-bridge/commits/main
[license-shield]: https://img.shields.io/github/license/VOTRE_USERNAME/hisense-mqtt-bridge?style=for-the-badge
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen?style=for-the-badge
[forum]: https://community.home-assistant.io/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
```

---

## Fichiers complémentaires à créer

### `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug report
about: Signaler un bug
title: '[BUG] '
labels: bug
assignees: ''
---

**Description du bug**
Une description claire et concise du bug.

**Reproduction**
Étapes pour reproduire le comportement :
1. Aller à '...'
2. Cliquer sur '....'
3. Voir l'erreur

**Comportement attendu**
Ce qui devrait se passer.

**Captures d'écran**
Si applicable, ajoutez des captures d'écran.

**Environnement:**
 - Version Home Assistant: [ex. 2024.1.0]
 - Version addon: [ex. 1.0.0]
 - Modèle TV: [ex. Hisense 55A7G]
 - Version Vidaa: [ex. U5]

**Logs**
```
Collez les logs ici
```

**Configuration**
```yaml
# Votre configuration (sans mots de passe)
```

**Informations complémentaires**
Tout autre contexte utile.
```

### `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature request
about: Suggérer une amélioration
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Problème résolu**
Quel problème cette fonctionnalité résoudrait-elle ?

**Solution proposée**
Description claire de ce que vous aimeriez voir.

**Alternatives considérées**
Autres solutions ou fonctionnalités envisagées.

**Informations complémentaires**
Tout autre contexte ou captures d'écran.
```

Voilà ! Tu as maintenant un README.md complet et professionnel pour ton dépôt GitHub ! 🎉📚