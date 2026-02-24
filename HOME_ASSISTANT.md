# Installation & Déploiement Home Assistant

Ce guide vous explique comment installer et configurer l'addon Hisense MQTT Bridge dans Home Assistant.

## Table des matières

- [Pré-requis](#pré-requis)
- [Installation rapide](#installation-rapide)
- [Configuration](#configuration)
- [Vérification du fonctionnement](#vérification-du-fonctionnement)
- [Intégration Home Assistant](#intégration-home-assistant)
- [Dépannage](#dépannage)

---

## Pré-requis

### 1. Home Assistant
- Version **2023.1+** recommandée
- Accès administrateur à l'interface

### 2. MQTT
- Broker MQTT fonctionnel (Mosquitto recommandé)
- Adresse IP du broker connue
- Port MQTT accessible (défaut: 1883)

### 3. Hisense TV Vidaa-U
- TV sur le même réseau que Home Assistant
- Adresse IP connue
- Port 10001 accessible (WebSocket)

### 4. Addons Home Assistant (pré-requis optionnels)
- **Mosquitto MQTT** (recommandé) - pour le broker
- **Studio Code Server** (optionnel) - pour les logs avancés

---

## Installation Rapide

### Étape 1: Ajouter le dépôt d'addon

1. Dans Home Assistant, allez à:
   ```
   Paramètres → Addons → Boutiques d'addons
   ```

2. Cliquez sur **Créer une boutique d'addon**

3. Entrez l'URL du dépôt:
   ```
   https://github.com/yourusername/hisense-mqtt-addon
   ```

4. Cliquez sur **Créer**

### Étape 2: Installer l'addon

1. Allez à:
   ```
   Paramètres → Addons → Boutique d'addons
   ```

2. Trouvez **Hisense TV MQTT Bridge** dans votre dépôt

3. Cliquez sur **Installer**

4. Attendez la fin du téléchargement et de la construction (2-5 minutes)

### Étape 3: Configuration de base

1. Allez à:
   ```
   Paramètres → Addons → Hisense TV MQTT Bridge
   ```

2. Sous **Configuration**, remplissez les champs obligatoires:
   - **TV IP**: Adresse IP de votre TV (ex: `192.168.1.100`)
   - **MQTT Broker**: Adresse IP de votre broker (ex: `192.168.1.10`)

3. Cliquez sur **Sauvegarder**

4. Cliquez sur **Démarrer**

---

## Configuration Complète

### Paramètres obligatoires

| Paramètre | Exemple | Description |
|-----------|---------|-------------|
| **TV IP** | `192.168.1.100` | Adresse IP de votre TV Hisense |
| **MQTT Broker** | `192.168.1.10` | Adresse de votre broker MQTT |

### Paramètres MQTT

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| MQTT Port | `1883` | Port du broker MQTT |
| MQTT User | (vide) | Nom d'utilisateur (optionnel) |
| MQTT Password | (vide) | Mot de passe (optionnel) |
| MQTT Topic Prefix | `hisense_tv` | Préfixe des topics MQTT |

### Paramètres TV

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| **TV Port** | `10001` | Port WebSocket (Vidaa-U standard) |
| TV Name | `salon` | Nom de la TV (pour MQTT) |
| TV SSL | `false` | Activer SSL (rarement nécessaire) |

### Paramètres avancés

| Paramètre | Défaut | Options | Description |
|-----------|--------|---------|-------------|
| Auto Discovery | `true` | true/false | Auto-découverte Home Assistant |
| Scan Interval | `30` | 10-300 | Intervalle de synchronisation (sec) |
| Log Level | `INFO` | DEBUG/INFO/WARNING/ERROR | Niveau de verbosité |

### Exemple de configuration

```yaml
TV IP: 192.168.1.100
TV Port: 10001
TV Name: salon
TV SSL: false

MQTT Broker: 192.168.1.10
MQTT Port: 1883
MQTT User: mqtt
MQTT Password: mypassword
MQTT Topic Prefix: hisense_tv

Auto Discovery: true
Scan Interval: 30
Log Level: INFO
```

---

## Vérification du Fonctionnement

### 1. Vérifier les logs

1. Allez à:
   ```
   Paramètres → Addons → Hisense TV MQTT Bridge → Logs
   ```

2. Cherchez ces messages de succès:
   ```
   ✅ Configuration loaded - TV IP: 192.168.1.100:10001
   🌐 Connecting to MQTT broker: 192.168.1.10:1883
   ✅ Connected to MQTT broker
   📡 Attempting connection: ws://192.168.1.100:10001
   ✅ Connected to ws://192.168.1.100:10001
   🔐 Handshake sent
   🔑 Encryption keys updated
   ✅ Bridge started successfully
   ```

### 2. Tester via MQTT

1. Ouvrez **Developer Tools → MQTT**

2. Abonnez-vous au topic:
   ```
   hisense_tv/salon/state/#
   ```

3. Vous devriez voir des mises à jour d'état toutes les 30 secondes

4. Envoyez une commande de test:
   ```
   Topic: hisense_tv/salon/command/volume
   Payload: up
   ```

5. Vérifiez que le volume change sur la TV

### 3. Vérifier l'intégration Home Assistant

1. Allez à:
   ```
   Paramètres → Appareils et services → MQTT
   ```

2. Vous devriez voir un appareil **Hisense TV salon**

3. Cliquez pour voir les entités disponibles:
   - Media Player
   - Power Switch
   - Volume Sensor
   - Source Sensor

---

## Intégration Home Assistant

### Auto-Découverte

L'addon publie automatiquement les configurations pour Home Assistant:

- **Media Player** - Contrôle complet de la TV
- **Power Switch** - Allumer/éteindre
- **Volume Sensor** - Niveau du volume
- **Mute Switch** - Couper/rétablir le son
- **Source Sensor** - Entrée actuelle

Les entités apparaissent automatically dans:
```
Paramètres → Appareils et services → MQTT
```

### Créer des automatisations

**Exemple 1: Allumer la TV à 20h**

```yaml
alias: "TV on at 8pm"
trigger:
  platform: time
  at: "20:00:00"
action:
  service: mqtt.publish
  data:
    topic: hisense_tv/salon/command/power
    payload: "on"
```

**Exemple 2: Éteindre quand personne n'est à la maison**

```yaml
alias: "TV off when away"
trigger:
  platform: state
  entity_id: group.family
  to: "not_home"
action:
  service: mqtt.publish
  data:
    topic: hisense_tv/salon/command/power
    payload: "off"
```

**Exemple 3: Notification si TV reste allumée 1h**

```yaml
alias: "TV on for too long"
trigger:
  platform: state
  entity_id: switch.hisense_tv_salon_power
  to: "on"
  for:
    hours: 1
action:
  service: notify.notify
  data:
    message: "TV has been on for 1 hour"
```

---

## Dépannage

### L'addon ne démarre pas

1. Vérifiez les logs:
   ```
   Paramètres → Addons → Hisense TV MQTT Bridge → Logs
   ```

2. Si erreur **TV_IP non défini**:
   - Allez à Configuration
   - Assurez-vous que **TV IP** est rempli
   - Cliquez Sauvegarder et redémarrez

3. Si erreur **MQTT not connected**:
   - Vérifiez que l'addresse MQTT est correcte
   - Assurez-vous que le broker MQTT est en marche
   - Vérifiez les pare-feu

### La TV ne se connecte pas

1. Vérifiez l'adresse IP de la TV:
   ```bash
   # Depuis Home Assistant
   ping 192.168.1.100
   ```

2. Vérifiez que la TV est allumée et connectée au réseau

3. Changez le port TV en mode débogage:
   - TV Port: `36669` (port alternatif)
   - Redémarrez l'addon
   - Vérifiez les logs

4. Activez le mode DEBUG:
   - Log Level: `DEBUG`
   - Redémarrez
   - Vérifiez les logs détaillés

### Les commandes ne passent pas

1. Vérifiez dans les logs que la connexion est stable:
   - Cherchez `✅ Connected`
   - Pas de `🔴 Connection closed`

2. Testez une commande simple:
   ```
   Topic: hisense_tv/salon/command/power
   Payload: on
   ```

3. Si c'est lent, augmentez le délai:
   - Scan Interval: `60` secondes
   - Redémarrez

### Les états ne se mettent pas à jour

1. Vérifiez le Scan Interval n'est pas trop long (par défaut 30s)

2. Activez DEBUG et cherchez `State updated:`

3. Vérifiez que votre TV prend en charge les mises à jour d'état:
   - C'est une limitation de certains modèles

---

## Commandes MQTT Disponibles

### Allumer/Éteindre
```
Topic: hisense_tv/salon/command/power
Payload: on | off | toggle
```

### Volume
```
Topic: hisense_tv/salon/command/volume
Payload: up | down | 0-100 (niveau spécifique)
```

### Muet
```
Topic: hisense_tv/salon/command/mute
Payload: (n'importe quelle valeur)
```

### Source
```
Topic: hisense_tv/salon/command/source
Payload: HDMI1 | HDMI2 | HDMI3 | HDMI4 | TV | AV
```

### Chaîne
```
Topic: hisense_tv/salon/command/channel
Payload: up | down | 1-999 (numéro spécifique)
```

### Navigation
```
Topic: hisense_tv/salon/command/navigate
Payload: UP | DOWN | LEFT | RIGHT | OK | BACK | HOME | MENU
```

---

## Support

### Voir les logs complets
```
Paramètres → Addons → Hisense TV MQTT Bridge → Logs
```

### Mode débogage
1. Allez à Configuration
2. Log Level: `DEBUG`
3. Cliquez Sauvegarder
4. Redémarrez l'addon
5. Vérifiez les logs détaillés

### Rapporter un problème

Incluez dans votre rapport:
1. Les logs complets (Mode DEBUG)
2. Votre modèle de TV
3. Votre version Home Assistant
4. La version de l'addon
5. Les étapes pour reproduire

---

## Mise à Jour

Les mises à jour sont disponibles automatiquement:

1. Allez à:
   ```
   Paramètres → Addons → Hisense TV MQTT Bridge
   ```

2. Si **Mettre à jour** est disponible, cliquez

3. Attendez la fin
   ```
   Redémarrer l'addon
   ```

---

## Configuration Avancée

Pour les utilisateurs avancés, vous pouvez aussi:

1. **Modifier les scripts de service** (nécessite SSH)
2. **Activer des logs supplémentaires**
3. **Utiliser des templates Jinja2** pour les automatisations

Consultez la documentation complète: `CONFIGURATION.md`

---

## Prochaines Étapes

✅ Addon installé et démarré  
✅ Configuration complétée  
✅ MQTT fonctionne  
✅ TV réagit aux commandes  

Maintenant vous pouvez:

1. Créer des **automatisations** avec la TV
2. Ajouter des **scripts** et **scènes**
3. Configurer des **notifications** intelligentes
4. Intégrer avec d'autres appareils (lumières, sons, etc.)

Bon contrôle! 🚀
