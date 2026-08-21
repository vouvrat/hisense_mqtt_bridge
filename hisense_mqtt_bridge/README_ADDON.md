# 📚 INDEX - Addon Home Assistant

## 🚀 COMMENCEZ ICI

**Nouveau avec cet addon?** Lisez dans cet ordre:

1. **[ADDON_READY.md](ADDON_READY.md)** ← LISEZ CECI EN PREMIER! (5 min)
   - Statut de déploiement
   - Ce qui a été corrigé
   - Comment déployer

2. **[HOME_ASSISTANT.md](HOME_ASSISTANT.md)** ← Guide d'installation (10 min)
   - Installation pas-à-pas
   - Configuration
   - Premier démarrage
   - Tests

3. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** ← Vérification (5 min)
   - Checklist complète
   - Structure GitHub
   - Déploiement options

---

## 📖 Documentation Par Type

### Pour Utilisateurs Finaux
- 📄 **[HOME_ASSISTANT.md](HOME_ASSISTANT.md)** 
  - Comment installer
  - Comment configurer
  - Troubleshooting

- 📄 **[CONFIGURATION.md](../CONFIGURATION.md)**
  - Toutes les options
  - Exemples MQTT
  - Home Assistant integration

### Pour Développeurs / DevOps
- 📄 **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
  - Checklist production
  - Structure GitHub
  - Pré-requis

---

## ✅ État Addon

| Aspect | Status | Notes |
|--------|--------|-------|
| **Structure** | ✅ Complète | Tous fichiers présents |
| **Configuration** | ✅ Corrigée | tv_ssl au lieu de ssl_enabled |
| **Port** | ✅ Correct | 10001 (Vidaa-U) |
| **Scripts** | ✅ Fonctionnels | run + finish scripts (services.d) OK |
| **Docker** | ✅ Ready | aarch64 + amd64 |
| **Documentation** | ✅ Complète | 100% en français |
| **Tests** | ⚠️ Manuels | Pas de suite de tests automatisée — voir tasks/historique.md pour l'audit de code |

---

## 🚀 Déploiement Rapide

### Téléchargement (2 min)
1. Dépôt GitHub : https://github.com/vouvrat/hisense_mqtt_bridge

### Installation Home Assistant (5 min)
1. Paramètres → Addons → Boutiques d'addons
2. URL du repo → Créer
3. Chercher "Hisense" → Installer
4. Configurer TV IP et MQTT Broker
5. Démarrer

### Vérification (2 min)
1. Vérifiez les logs
2. Cherchez ✅ `Bridge started successfully`
3. Testez une commande MQTT

**Total: ~15 minutes du start au succès! ⏱️**

---

## 🔧 Structure Addon Home Assistant

```
hisense_mqtt_bridge/
├── config.yaml              ← Configuration UI
├── Dockerfile               ← Image Docker
├── build.yaml               ← Build config
├── requirements.txt         ← Dépendances Python (source unique)
├── rootfs/
│   ├── app/
│   │   └── hisense_mqtt_bridge.py   ← Application
│   └── etc/services.d/
│       └── hisense-mqtt/
│           ├── run         ← Script démarrage
│           └── finish      ← Script arrêt
└── [Documentation principale au niveau parent]
```

---

## 📋 Fichiers de Configuration

### config.yaml (Important!)
```yaml
name: "Hisense TV MQTT Bridge"
version: "2.0.0"
slug: hisense_mqtt_bridge
arch:
  - aarch64
  - amd64

options:
  tv_ip: ""                           # OBLIGATOIRE
  tv_port: 10001                      # Default Vidaa-U
  tv_ssl: false                       # Nouveau (pas ssl_enabled!)
  mqtt_broker: ""                     # OBLIGATOIRE
  mqtt_port: 1883
  mqtt_user: ""
  mqtt_password: ""
  # ... rest
```

### Important: Variables
- ✅ `tv_ssl` (booléen) - Utilisé maintenant
- ❌ `ssl_enabled` - ANCIEN, supprimé
- ✅ `tv_port` par défaut: 10001 - Vidaa-U standard

---

## 🧪 Tests d'Installation

### Test 1: Structure Addon (2 min)
```bash
cd hisense_mqtt_bridge
ls -la config.yaml Dockerfile rootfs/
# Doit afficher tous les fichiers
```

### Test 2: Configuration (1 min)
```bash
# Vérifier les paramètres clés
grep "tv_port: 10001" config.yaml
grep "tv_ssl:" config.yaml
# Ne doit pas avoir ssl_enabled
```

### Test 3: Python (1 min)
```bash
# Vérifier la syntaxe
python3 -m py_compile rootfs/app/hisense_mqtt_bridge.py
# Doit réussir sans erreur
```

### Test 4: Scripts (1 min)
```bash
# Vérifier les permissions
ls -la rootfs/etc/services.d/hisense-mqtt/run
# Doit être exécutable (x)
```

---

## 🆘 Aide Rapide

| Problème | Solution |
|----------|----------|
| Addon ne démarre pas | Vérifiez TV_IP et MQTT_BROKER configurés |
| La TV ne se connecte pas | Vérifiez TV_IP est correct, port 10001 accessible |
| MQTT "not connected" | Vérifiez MQTT_BROKER et port |
| Pas d'états | Attendez 30s (scan interval), puis recheckez |
| Erreur configuration | Activez DEBUG et vérifiez les logs |

Pour plus d'aide → **[HOME_ASSISTANT.md - Troubleshooting](HOME_ASSISTANT.md#dépannage)**

---

## 📊 Checklist Avant Production

- [ ] J'ai lu ADDON_READY.md
- [ ] J'ai lu HOME_ASSISTANT.md
- [ ] J'ai créé le repository GitHub
- [ ] J'ai ajouté l'addon repository à HA
- [ ] J'ai installé l'addon
- [ ] J'ai configuré TV IP et MQTT Broker
- [ ] J'ai démarré l'addon avec succès
- [ ] J'ai vu "✅ Bridge started successfully" dans les logs
- [ ] J'ai testé au moins une commande MQTT
- [ ] Les entités Home Assistant sont visibles

**Tous cochés?** → Déploiement réussi! 🎉

---

## 🎯 Fichiers Par Besoin

### "Je veux juste installer"
→ **[HOME_ASSISTANT.md](HOME_ASSISTANT.md)**

### "Je veux comprendre les changements"
→ **[ADDON_READY.md](ADDON_READY.md)** + tasks/historique.md (audit et corrections)

### "Je dois vérifier que c'est OK"
→ **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**

### "Je dois déployer sur GitHub"
→ **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Section GitHub

### "J'ai un problème!"
→ **[HOME_ASSISTANT.md - Troubleshooting](HOME_ASSISTANT.md#dépannage)**

### "Je dois configurer MQTT"
→ **[CONFIGURATION.md](../CONFIGURATION.md)**

---

## 🚀 Prochaines Étapes

### 1. Lire (15 min)
- [ ] ADDON_READY.md
- [ ] HOME_ASSISTANT.md jusqu'à "Installation rapide"

### 2. Créer (5 min)
- [ ] Créer repository GitHub
- [ ] Pousser les fichiers
- [ ] Vérifier le contenu

### 3. Installer (10 min)
- [ ] Ajouter repository à Home Assistant
- [ ] Installer l'addon
- [ ] Configurer les paramètres

### 4. Tester (5 min)
- [ ] Démarrer l'addon
- [ ] Vérifier les logs
- [ ] Tester une commande

### 5. Utiliser (∞)
- [ ] Créer des automatisations
- [ ] Intégrer d'autres appareils
- [ ] Share avec communauté HA! 🌟

---

## 📚 Ressources

Pour Home Assistant:
- [Official Addons Docs](https://developers.home-assistant.io/docs/add-ons_index)
- [MQTT Integration](https://www.home-assistant.io/integrations/mqtt/)
- [Community](https://community.home-assistant.io/)

Pour ce projet:
- Docs dans ce dossier et au niveau parent
- Historique des audits/corrections: tasks/historique.md
- Code principal: rootfs/app/hisense_mqtt_bridge.py

---

## 🎊 Status Final

```
✅ ADDON PRÊT POUR HOME ASSISTANT

✅ Configuration complète
✅ Fichiers corrects
⚠️ Validation manuelle (pas de suite de tests automatisée)
✅ Documentation française
✅ aarch64 + amd64

👉 Lisez ADDON_READY.md pour commencer!
```

---

**Updated:** 21 août 2026 (revue documentation)
**Version:** 2.0.0

Pour commencer: **[ADDON_READY.md](ADDON_READY.md)**
