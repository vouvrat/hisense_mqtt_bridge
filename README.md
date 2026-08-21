# Hisense TV MQTT Bridge

Home Assistant add-on that bridges a Hisense VIDAA-U TV to MQTT.
Add-on Home Assistant qui relie une TV Hisense VIDAA-U à MQTT.

[🇫🇷 Français](#français) · [🇬🇧 English](#english)

[![Open your Home Assistant instance and show the add-on repository dialog.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fvouvrat%2Fhisense_mqtt_bridge)

---

## Français

### Présentation

Cet add-on se connecte à une TV Hisense VIDAA-U en WebSocket (détection
automatique du port : `10001`, `36669`, `36670`, `36870`) et expose son état
et ses commandes sur MQTT, avec auto-découverte Home Assistant.

### Fonctionnalités

**Entités Home Assistant auto-découvertes** (via MQTT Discovery) :
- Media Player (contrôle power)
- Switch Power
- Sensor Volume

**Autres commandes disponibles** via publication MQTT brute sur les topics
`command/*` (pas encore d'entité HA dédiée) : mute, source, chaîne,
navigation, touche IR brute. Détail complet des topics dans
[CONFIGURATION.md](CONFIGURATION.md).

### Architecture supportée

`aarch64`, `amd64` — voir [tasks/historique.md](tasks/historique.md) pour
le détail de ce choix (image de base Home Assistant à jour, non disponible
pour les architectures 32 bits).

### Prérequis

- Home Assistant avec Supervisor
- Un broker MQTT (Mosquitto ou autre)
- Une TV Hisense VIDAA-U sur le même réseau

### Installation rapide

1. Cliquez sur le bouton ci-dessus, ou ajoutez ce dépôt manuellement :
   `Paramètres → Add-ons → Boutique des add-ons → ⋮ → Dépôts` puis
   `https://github.com/vouvrat/hisense_mqtt_bridge`
2. Installez **Hisense TV MQTT Bridge**
3. Configurez `tv_ip` et `mqtt_broker` (champs obligatoires)
4. Démarrez l'add-on

Guide détaillé : [HOME_ASSISTANT.md](HOME_ASSISTANT.md)

### Documentation

| Document | Contenu |
|---|---|
| [HOME_ASSISTANT.md](HOME_ASSISTANT.md) | Guide d'installation et de dépannage |
| [CONFIGURATION.md](CONFIGURATION.md) | Référence complète : variables, topics MQTT, exemples |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Checklist de déploiement |
| [ADDON_READY.md](ADDON_READY.md) | Historique des changements pour Home Assistant |
| [hisense_mqtt_bridge/README_ADDON.md](hisense_mqtt_bridge/README_ADDON.md) | Index de la documentation de l'add-on |
| [tasks/historique.md](tasks/historique.md) | Audit de code complet et historique des corrections |
| [LICENCE](LICENCE) | Licence MIT |

### État du projet

Le projet a fait l'objet d'un audit de code complet (29 points relevés :
4 critiques, 14 majeurs, 11 mineurs), tous corrigés. Détail intégral,
raisonnement et vérifications dans [tasks/historique.md](tasks/historique.md).
Non vérifié à ce jour : build Docker réel et connexion à une TV/broker MQTT
réels — à valider sur un déploiement Home Assistant.

### Licence

[MIT](LICENCE)

---

## English

### Overview

This add-on connects to a Hisense VIDAA-U TV over WebSocket (automatic
port detection: `10001`, `36669`, `36670`, `36870`) and exposes its state
and commands over MQTT, with Home Assistant auto-discovery.

### Features

**Auto-discovered Home Assistant entities** (via MQTT Discovery):
- Media Player (power control)
- Power switch
- Volume sensor

**Other commands** available via raw MQTT publish on `command/*` topics
(no dedicated HA entity yet): mute, source, channel, navigation, raw IR
key. Full topic reference in [CONFIGURATION.md](CONFIGURATION.md).

### Supported architecture

`aarch64`, `amd64` — see [tasks/historique.md](tasks/historique.md) for
why (current Home Assistant base image isn't published for 32-bit
architectures).

### Requirements

- Home Assistant with Supervisor
- An MQTT broker (Mosquitto or other)
- A Hisense VIDAA-U TV on the same network

### Quick install

1. Click the button above, or add this repository manually:
   `Settings → Add-ons → Add-on Store → ⋮ → Repositories` then
   `https://github.com/vouvrat/hisense_mqtt_bridge`
2. Install **Hisense TV MQTT Bridge**
3. Configure `tv_ip` and `mqtt_broker` (required fields)
4. Start the add-on

Full guide: [HOME_ASSISTANT.md](HOME_ASSISTANT.md)

### Documentation

| Document | Content |
|---|---|
| [HOME_ASSISTANT.md](HOME_ASSISTANT.md) | Install & troubleshooting guide |
| [CONFIGURATION.md](CONFIGURATION.md) | Full reference: variables, MQTT topics, examples |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Deployment checklist |
| [ADDON_READY.md](ADDON_READY.md) | Home Assistant changelog |
| [hisense_mqtt_bridge/README_ADDON.md](hisense_mqtt_bridge/README_ADDON.md) | Add-on documentation index |
| [tasks/historique.md](tasks/historique.md) | Full code audit trail and fix history |
| [LICENCE](LICENCE) | MIT License |

### Project status

The project went through a full code audit (29 findings: 4 critical, 14
major, 11 minor), all fixed. Full detail, reasoning and verification notes
in [tasks/historique.md](tasks/historique.md). Not yet verified: a real
Docker build and a real TV/MQTT-broker connection — pending validation on
an actual Home Assistant deployment.

### License

[MIT](LICENCE)
