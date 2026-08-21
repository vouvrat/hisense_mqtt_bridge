# Historique

Format : entrée datée par intervention (analyse, correction, décision).

---

## [2026-08-21] Audit complet qualité / sécurité / architecture

**Contexte** : première prise en main du projet après clonage. Demande d'un
audit exhaustif (bons points, mauvais points, corrections avec quoi/pourquoi/
comment) avant toute intervention sur le code. Réalisé en lecture seule par
un sous-agent dédié ayant lu intégralement les 850 lignes de
`hisense_mqtt_bridge.py`, tous les fichiers de config/build, les scripts s6,
et les 5 documents Markdown, avec vérifications croisées (grep, comparaison
config↔code, git log).

Le git log révélait déjà un pattern d'alerte : plusieurs commits "Fix:"
répétés sur les mêmes problèmes (TV_PORT non lu × 2, fins de ligne, export
env vars, build local vs image pré-construite, "Restructuration pour
compatibilité Home Assistant" × 3). L'audit confirme que certains de ces
correctifs sont solides (fins de ligne, mapping config↔env vars) mais que
la restructuration répétée a laissé des reliquats (P12) et que d'autres
classes de bugs similaires n'ont jamais été traitées (P1-P3, P8-P9).

### Bons points

- Structure d'addon HA conforme à la spec s6-overlay (`init: false`, build
  local cohérent avec `build.yaml` multi-arch).
- Mapping `config.yaml` ↔ variables d'environnement ↔ `load_config()`
  cohérent sur les 12 clés — le bug historique "TV_PORT non lu" semble
  réellement corrigé, pas de nouvelle divergence.
- Fins de ligne saines partout (LF), le problème CRLF historique est résolu.
- Secrets (mqtt_password/user) jamais loggés ; `password?` dans le schema HA
  masque bien le champ dans l'UI.
- Pattern MQTT idiomatique : Last Will/Testament, QoS 1 + retain, discovery
  publié après connexion — conforme aux conventions HA.
- Gestion d'erreurs systématique (try/except sur quasi toutes les méthodes
  réseau), threads en mode daemon.
- Détection multi-port pragmatique pour un protocole non documenté.
- Séparation claire `HisenseTV` / `MQTTBridge`, code lisible, bien docstring.

### Problèmes identifiés (29 au total)

**Critiques (4)**
| # | Problème | Fichier:ligne |
|---|---|---|
| P1 | Le bridge s'arrête complètement si la TV ne répond pas en 10s au démarrage (cas pourtant très fréquent — TV éteinte) | `hisense_mqtt_bridge.py:780-796` |
| P2 | `main()` ignore le retour de `run()` → exit code 0 même en cas d'échec, masque toute panne à s6 | `hisense_mqtt_bridge.py:839-847` |
| P3 | Aucun backoff : si MQTT est injoignable au démarrage, boucle de crash rapide (s6 relance sans délai) | `hisense_mqtt_bridge.py:466-502`, `rootfs/etc/services.d/hisense-mqtt/finish` |
| P4 | `LICENCE` vide (0 octet) — dépôt public destiné à un addon store HA sans droits accordés légalement | `LICENCE` |

**Majeurs (14)**
| # | Problème | Fichier:ligne |
|---|---|---|
| P5 | `power_on()`/`power_off()` envoient la même touche toggle → risque d'allumer une TV qu'on voulait éteindre | `hisense_mqtt_bridge.py:344-350` |
| P6 | Pas de lock autour de `self.ws.send()`/`self.connected`, accédés par plusieurs threads | `hisense_mqtt_bridge.py:320-333, 745-778, 523-536` |
| P7 | Race condition dans le balayage multi-port de `connect()` | `hisense_mqtt_bridge.py:104-183` |
| P8 | Timeout désynchronisé : `setup_tv()` abandonne à 10s, le thread de scan continue ~20s de plus | `hisense_mqtt_bridge.py:729-732` |
| P9 | Fuite de threads/sockets sur reconnexions répétées (pas de `join()`/fermeture de l'ancien `HisenseTV`) | `hisense_mqtt_bridge.py:716-728` |
| P10 | `requirements.txt` désynchronisé des versions réellement installées par le `Dockerfile`, et jamais utilisé au build | `requirements.txt` vs `Dockerfile:18-23` |
| P11 | Dépendances installées inutilisées : `requests`, et `asyncio` (backport PyPI incompatible Python 3.11) | `Dockerfile:18-23` |
| P12 | `run.sh` à la racine de l'addon : code mort, doublon du vrai point d'entrée s6, la doc le cite à tort comme "point d'entrée" | `hisense_mqtt_bridge/run.sh` |
| P13 | Doc référence des fichiers inexistants (`TESTING.md`, `DOCKER.md`, scripts de test...) avec de faux résultats de tests | `README_ADDON.md`, `DEPLOYMENT_CHECKLIST.md`, `ADDON_READY.md` |
| P14 | Doc annonce un "Mute Switch" et un "Source Sensor" jamais publiés par `_publish_discovery()` | `CONFIGURATION.md`, `HOME_ASSISTANT.md` vs `hisense_mqtt_bridge.py:640-714` |
| P15 | `hassio_api`/`homeassistant_api: true` déclarés sans aucun usage dans le code — sur-permissionnement | `config.yaml:14-15` |
| P16 | Image de base Alpine 3.18 (mai 2023), ~3 ans de retard sécurité | `build.yaml:1-6` |
| P17 | `tv_name` (chaîne libre) non assaini avant usage dans topics MQTT / identifiants HA discovery | `hisense_mqtt_bridge.py:461-464, 644-712` |
| P18 | Description "support complet du protocole" trompeuse : navigation/source/chaîne non pilotables via entités HA, MQTT brut uniquement | `config.yaml:4` |

**Mineurs (11)** : imports inutilisés `hashlib`/`socket` (P19) · parsing int() avant init du logger (P20) · logs DEBUG verbeux (P21) · TLS TV désactivé sans commentaire justificatif (P22) · pas de typage des valeurs reçues de la TV (P23) · `apk add python3 py3-pip` redondant avec l'image de base (P24) · `mosquitto-clients`/`jq` installés mais inutilisés (P25) · URL repository.yaml incohérente avec la doc (placeholder jamais remplacé) (P26) · paho-mqtt épinglé 1.6.1 sans commentaire expliquant pourquoi (API v1 vs v2) (P27) · `tv_ip` "obligatoire" mais une valeur par défaut plausible contourne la validation (P28) · dates de doc figées à février 2025, jamais remises à jour (P29).

### Corrections recommandées (résumé — détail complet dans le rapport agent)

1. **P1+P2+P3 (robustesse démarrage)** — ne plus interrompre `run()` sur échec
   TV (démarrer `state_monitor` quand même, publier `offline`), tester le
   retour de `bridge.run()` dans `main()` avec `sys.exit(1)`, ajouter un
   backoff avant tout exit fatal.
2. **P4 (licence)** — ajouter un vrai texte de licence (MIT/Apache-2.0/GPL
   au choix de l'auteur).
3. **P5 (power toggle)** — vérifier l'état connu avant d'envoyer `KEY_POWER`
   dans `power_on`/`power_off`, sur le modèle du `toggle` déjà correct.
4. **P6+P7 (concurrence)** — `threading.Lock()` autour de `self.ws`/
   `self.connected`, isoler chaque tentative de port avec des variables
   locales dans `connect()`.
5. **P8+P9 (timeout/fuite)** — fermer l'ancien `HisenseTV` avant d'en
   recréer un, aligner les timeouts.
6. **P10+P11 (dépendances)** — synchroniser ou supprimer `requirements.txt`,
   retirer `requests`/`asyncio` du Dockerfile.
7. **P12 (run.sh mort)** — `git rm hisense_mqtt_bridge/run.sh`, corriger la
   doc qui le cite comme point d'entrée.
8. **P13+P14+P18 (doc trompeuse)** — purger les références à des fichiers
   inexistants, aligner la liste des entités documentées sur
   `_publish_discovery()` réel.
9. **P15 (permissions HA)** — retirer `hassio_api`/`homeassistant_api` de
   `config.yaml`.
10. **P16 (image obsolète)** — mettre à jour `build.yaml` vers une base
    Alpine récente.
11. **P17 (tv_name non assaini)** — slugifier avant usage dans les topics/
    identifiants.

**Décision** : analyse uniquement à ce stade, aucune modification de code
effectuée. Prochaine étape à définir avec l'utilisateur — priorisation
probable : critiques (P1-P4) d'abord, puis majeurs.

---

## [2026-08-21] Correction des 4 problèmes critiques (P1-P4)

**P1 — Bridge s'arrêtait si la TV ne répondait pas au démarrage**
`hisense_mqtt_bridge.py` (`run()`, ~ligne 793) : l'échec de `setup_tv()`
n'est plus fatal. Un warning est loggué, `offline` est publié sur le topic
availability, et `state_monitor` démarre quand même (il gère déjà la
reconnexion périodique). Seul un échec de `setup_mqtt()` reste fatal.

**P2 — `main()` ignorait le retour de `run()` (exit code toujours 0)**
`hisense_mqtt_bridge.py` (`main()`, ~ligne 839) : le retour de
`bridge.run()` est maintenant testé ; `sys.exit(1)` en cas d'échec, avec
message d'erreur explicite.

**P3 — Absence de backoff (risque de boucle de crash rapide)**
Deux niveaux, comme recommandé par l'audit :
- Python : `time.sleep(10)` avant chaque `sys.exit(1)` dans `main()`
  (échec de démarrage et exception fatale).
- s6 : `s6-sleep 10` ajouté dans
  `rootfs/etc/services.d/hisense-mqtt/finish` avant
  `s6-svscanctl -t /var/run/s6/services`, pour garantir un délai minimal
  entre un arrêt du service et le redémarrage déclenché par s6.

**P4 — `LICENCE` vide**
Licence choisie par l'utilisateur : **MIT**. Texte complet écrit dans
`LICENCE` (copyright Vincent, 2026).

**Vérification effectuée** :
- `python3 -m py_compile hisense_mqtt_bridge.py` → syntaxe valide.
- Relecture manuelle de la logique modifiée (`run()`/`main()`) — cohérente
  avec le comportement attendu (démarrage résilient, exit code correct,
  backoff en place).
- `git diff --stat` : 3 fichiers modifiés, changements ciblés (pas
  d'effet de bord sur du code non concerné par P1-P4).

**Limite de vérification (à noter explicitement, honnêtement)** : aucun
test bout en bout n'a été effectué (pas de TV Hisense physique ni de
broker MQTT disponible dans cet environnement). Le comportement réel en
conditions de démarrage à froid (TV éteinte, broker injoignable) devra être
validé par l'utilisateur en déploiement réel sur son instance Home
Assistant avant de considérer P1-P3 comme pleinement vérifiés.

**Non traité à ce stade** : les 14 problèmes majeurs et 11 mineurs restent
dans le backlog (tasks/todo.md), en attente de priorisation.

---

## [2026-08-21] Correction des 14 problèmes majeurs (P5-P18)

**Analyse de risque préalable** (demandée explicitement par l'utilisateur
avant de commencer) : 3 des 14 majeurs touchent directement le code modifié
pour P1-P4 — P8-P9 réécrivent `setup_tv()` (appelée par `run()` en mode non
fatal depuis P1), P6-P7 réécrivent `HisenseTV.connect()`/`_send_command()`
dont dépend `setup_tv()`, et P17 touche `__init__` qui construit
`self.availability_topic` utilisé par le code `offline` ajouté en P1. Les
11 autres (P5, P10-P16, P18) sont isolés de cette zone. Travail fait dans
cet ordre, avec relecture ciblée de `run()`/`main()` après le lot à risque.

### P5 — power_on/power_off toggle unique
`HisenseTV.power_on()`/`power_off()` (~ligne 344) vérifient maintenant
`self.state['power']` avant d'envoyer `KEY_POWER` : n'envoient la touche
que si l'état cible diffère de l'état connu. Évite d'allumer une TV qu'on
voulait éteindre (et inversement).

### P17 — tv_name non assaini
Ajout de `self.safe_name` dans `MQTTBridge.__init__` (slugifié via
`re.sub(r'[^a-zA-Z0-9_-]', '_', ...)`), utilisé pour tous les topics MQTT
et identifiants HA discovery (`base_topic`, `client_id`, `identifiers`,
`unique_id`, chemins `homeassistant/.../config`). `config['tv_name']`
original conservé uniquement pour les champs d'affichage (`"name"`).

### P6-P7 — concurrence WebSocket
- **P6** : ajout de `self._send_lock = Lock()` (import `Lock` depuis
  `threading`), `_send_command()` protège la vérification `connected`/`ws`
  et l'appel `ws.send()` — plusieurs threads (commande MQTT, polling
  périodique) pouvaient appeler `ws.send()` concurremment.
- **P7** : `_on_open`/`_on_error`/`_on_close` vérifient maintenant
  `if ws is not self.ws: return` avant de modifier `self.connected` —
  empêche un callback tardif d'une tentative de port abandonnée (scan
  multi-port de `connect()`) d'écraser l'état de la tentative en cours.
  Fix minimal par garde d'identité plutôt que restructuration complète de
  la boucle de scan.

### P8-P9 — timeout désynchronisé + fuite de threads/sockets
`setup_tv()` (~ligne 743) :
- Ferme la connexion précédente (`self.tv.disconnect()`) avant d'en
  recréer une nouvelle — évite l'accumulation de threads/sockets orphelins
  sur des reconnexions répétées (`state_monitor()` rappelle `setup_tv()`
  en boucle).
- Timeout d'attente porté de 10s à 35s, aligné sur le pire cas réel de
  `connect()` (jusqu'à 5 ports × (5s + 1s) = 30s + marge).
- **Régression identifiée et corrigée pendant l'implémentation** : porter
  le timeout à 35s aurait retardé `stop()` jusqu'à 35s si un arrêt était
  demandé pendant l'attente (le thread `state_monitor` bloquait dans cette
  boucle sans vérifier l'arrêt demandé). Ajout de `self.running` dans la
  condition de la boucle d'attente pour sortir immédiatement si `stop()`
  est appelé.

**Vérification post-lot risqué** : `py_compile` + relecture complète de
`run()`/`main()`/`stop()` — confirmé que `setup_tv()` conserve son contrat
de retour booléen, P1-P4 inchangés et fonctionnels.

### P16 — image de base Alpine obsolète
Investigation via l'API GHCR (pas de supposition) : l'image actuelle
(`ghcr.io/home-assistant/amd64-base-python` et ses variantes par
architecture) est gelée depuis décembre 2024 au maximum
`3.12-alpine3.18` — l'audit initial supposait à tort qu'un simple
changement de tag suffirait. Une nouvelle image multi-arch existe
(`ghcr.io/home-assistant/base-python:3.14-alpine3.24`, vérifiée publiée le
19/08/2026, confirmée basée sur s6-overlay via `Entrypoint: ["/init"]` et
les variables `S6_*`), mais ne couvre que `amd64`/`arm64` — pas
`armv7`/`armhf`/`i386`. Question posée à l'utilisateur (vrai compromis
sécurité vs compatibilité matérielle) : **choix = basculer vers la
nouvelle image**, `armv7`/`armhf`/`i386` retirés de `config.yaml`
(`arch:`) et `build.yaml`.

### P10-P11 — dépendances mortes/incohérentes
`requirements.txt` déplacé de la racine du dépôt vers
`hisense_mqtt_bridge/` (il était hors du contexte de build Docker, donc
invisible/inutilisable pour le `Dockerfile` — cause racine de la
divergence). Contenu synchronisé (paho-mqtt 1.6.1, websocket-client
1.6.4, pycryptodome 3.19.0 — `requests` et `asyncio` retirés, jamais
utilisés dans le code). `Dockerfile` modifié pour `COPY` + `pip install -r
requirements.txt` au lieu d'une liste codée en dur : source unique de
vérité, évite que ce bug ne revienne. `paho-mqtt` intentionnellement
laissé en 1.6.1 (API callback v1, correspond aux signatures utilisées dans
le code — pas un oubli).

**Auto-correction pendant l'implémentation** : une première version de ce
changement supprimait aussi `python3`/`py3-pip`/`mosquitto-clients`/`jq`
de l'`apk add` (redondance avec l'image de base, P24/P25 — non demandé).
Corrigé immédiatement : ces paquets système sont hors du périmètre des 14
majeurs demandés et leur suppression n'est pas vérifiable sans build
Docker réel (indisponible ici) — restaurés.

### P12 — run.sh mort
`hisense_mqtt_bridge/run.sh` supprimé (`git rm`) après confirmation qu'il
n'était référencé par aucun fichier de build/manifest (grep) et qu'il est
fonctionnellement équivalent (en moins bien : pas de `python3 -u`) au vrai
point d'entrée `rootfs/etc/services.d/hisense-mqtt/run`.

### P13-P14-P18 — documentation obsolète/trompeuse
`README_ADDON.md`, `ADDON_READY.md`, `DEPLOYMENT_CHECKLIST.md` corrigés :
- Retrait de toutes les références à des fichiers inexistants
  (`TESTING.md`, `REFACTORING.md`, `DOCKER.md`, `test_addon.sh`,
  `test_integration.sh`, `quick_test.sh`, `validate_install.py`).
- Retrait des faux résultats de tests (« Results: 5 passed, 0 failed »),
  remplacés par une mention honnête : pas de suite de tests automatisée,
  validation = revue de code manuelle (renvoi vers ce fichier).
- Liste des entités HA corrigée partout : media_player, switch power,
  sensor volume uniquement (retrait des mentions de switch mute et sensor
  source, jamais publiés par `_publish_discovery()`).
- Liste d'architectures corrigée partout : aarch64/amd64 (cohérent avec
  P16).
- URL du dépôt placeholder (`yourusername/hisense-mqtt-addon`) remplacée
  par l'URL réelle (`vouvrat/hisense_mqtt_bridge`).
- Références à `run.sh` (supprimé en P12) remplacées par le vrai point
  d'entrée, avec note explicative.
- `config.yaml` : description corrigée (P18) — ne prétend plus à un
  « support complet du protocole », précise que le contrôle
  mute/source/chaîne/navigation passe par des topics MQTT bruts, pas des
  entités HA natives.
- Dates de mise à jour corrigées (au lieu de rester figées à février 2025).

**Vérification finale** :
- `python3 -m py_compile` sur `hisense_mqtt_bridge.py` → syntaxe valide.
- Relecture manuelle de `config.yaml`/`build.yaml` (pas de `pyyaml`/`pip`
  disponible dans cet environnement pour une validation automatisée —
  vérification visuelle de l'indentation/structure à la place, dit
  explicitement plutôt que prétendre à une validation automatisée qui n'a
  pas eu lieu).
- Recherche exhaustive (`grep`) de références mortes restantes dans les 3
  fichiers de documentation corrigés → aucune (hors mentions historiques
  explicites du type « n'a jamais existé »/« supprimé »).
- `git diff --stat` : 10 fichiers modifiés (+ 1 renommé, + 1 supprimé),
  changements cohérents avec le périmètre P5-P18.

**Non vérifié** (identique au lot critique) : build Docker réel, connexion
TV/MQTT réelle — nécessite un déploiement sur instance Home Assistant.

**Décisions utilisateur enregistrées** : licence MIT (lot critique),
bascule vers l'image multi-arch à jour avec abandon des architectures
32 bits (ce lot).

**Non traité à ce stade** : les 11 problèmes mineurs (P19-P29) restent dans
le backlog.

---

## [2026-08-21] Correction des 11 problèmes mineurs (P19-P29)

**Analyse de risque préalable** : P23 (typage volume) touche
`_update_state()`, qui alimente le sensor volume HA et est adjacente à la
ligne `power` dont dépend P5 — vérifié que cette ligne n'est pas modifiée.
P20 (validation int) touche `load_config()`, exécutée avant toute autre
logique — vérifié que `CONFIG` garde la même forme pour des entrées
valides. P24 (suppression `python3`/`py3-pip` du Dockerfile) vérifié en
lisant le Dockerfile source officiel de `home-assistant/docker-base` sur
GitHub (`python/3.14/Dockerfile`) : l'image de base compile Python et
installe pip via `ensurepip`, avec symlinks `python3`/`pip3` — confirmé,
pas supposé.

### P19 — imports morts
`hashlib` et `socket` retirés des imports (confirmé inutilisés par grep,
y compris après tous les changements des lots précédents).

### P20 — validation claire des variables d'environnement entières
Nouvelle fonction `_env_int(name, default)` dans le module, utilisée pour
`mqtt_port`, `tv_port`, `scan_interval` dans `load_config()`. Message
d'erreur explicite sur stderr + `sys.exit(1)` au lieu d'un traceback
Python brut si la valeur n'est pas un entier valide (le logger n'est pas
encore configuré à ce stade du démarrage, d'où l'écriture directe sur
stderr plutôt qu'un `logger.error`).

### P21 — logs DEBUG verbeux
Les 2 logs DEBUG qui n'étaient pas tronqués (`_send_command`,
`_on_mqtt_message`) tronqués à 200 caractères, cohérent avec le pattern
déjà utilisé ailleurs dans le fichier (`_on_message`).

### P22 — TLS sans justification
Commentaire ajouté avant le bloc `sslopt`/`CERT_NONE` : certificat
auto-signé de la TV, désactivation intentionnelle, acceptable car
connexion cantonnée au réseau local.

### P23 — typage du volume reçu de la TV
`_update_state()` coerce désormais `data.get('volume')` en `int` avec
`try/except`, log un warning si la valeur est inattendue plutôt que de
stocker une valeur potentiellement incohérente avec le sensor HA
`unit_of_measurement: "%"`. Ligne `power` (dont dépend P5) non touchée,
vérifié par relecture.

### P24-P25 — Dockerfile : dépendances système
`python3`/`py3-pip` retirés (redondants avec l'image de base, vérifié via
le Dockerfile source amont). `mosquitto-clients`/`jq` retirés (confirmés
inutilisés par grep dans le code et tous les scripts). `openssl`/`tzdata`
conservés (hors périmètre, pas de preuve de redondance).

### P26 — URL placeholder + liste d'entités fausse restantes
Le lot P13-P14 n'avait corrigé que README_ADDON.md/ADDON_READY.md/
DEPLOYMENT_CHECKLIST.md. En traitant P26, découverte que HOME_ASSISTANT.md
et CONFIGURATION.md avaient le même défaut non corrigé (URL placeholder
`yourusername/hisense-mqtt-addon`, liste d'entités mentionnant un switch
Mute et un sensor Source inexistants). Corrigés dans les deux fichiers
pour cohérence — c'est le même défaut déjà établi comme faux en P14,
pas une nouvelle extension de périmètre. Corrigé aussi dans ADDON_READY.md
une incohérence introduite par le lot précédent : l'« Étape 1 » disait
encore de créer un nouveau repository `hisense-mqtt-addon` alors que
l'« Étape 2 », déjà corrigée, indiquait que le dépôt réel existait déjà.

### P27 — paho-mqtt sans justification de version
Commentaire ajouté en tête de `requirements.txt` expliquant pourquoi
1.6.x est intentionnel (API callback v1, signatures utilisées dans le
code) et ce qui casserait avec un bump naïf vers 2.x.

### P28 — tv_ip par défaut contournait la validation "obligatoire"
`config.yaml` : `tv_ip` par défaut passé de `"192.168.1.100"` à `""`. Le
schema (`tv_ip: str`, sans `?`) et la validation bashio du script `run`
(`bashio::var.is_empty`) forcent maintenant réellement l'utilisateur à
configurer sa TV au lieu de démarrer silencieusement sur une IP par
défaut plausible mais fausse.
**Observation notée, non corrigée (hors périmètre strict de P28)** :
`mqtt_broker` a exactement le même défaut « plausible » (`192.168.1.10`)
et le même schema `str` obligatoire — même défaut potentiel, à traiter si
souhaité dans une prochaine passe.

### P29 — dates obsolètes
Recherche exhaustive (`grep`) : plus aucune date « Février 24, 2025 »
présentée comme actuelle, plus aucune URL placeholder
`yourusername`/`hisense-mqtt-addon` dans le dépôt.

**Vérification finale** :
- `python3 -m py_compile` → syntaxe valide.
- Relecture complète de `run()`/`stop()`/`main()` → P1-P4 et P5-P18
  inchangés et fonctionnels après ce lot.
- Recherche exhaustive de `hashlib.`/`socket.`/`mosquitto-clients`/`jq`/
  `yourusername` → aucune occurrence réelle restante (faux positifs
  attendus sur `WebSocketApp` et le commentaire explicatif écartés).

**Non vérifié** (identique aux lots précédents) : build Docker réel,
connexion TV/MQTT réelle.

**Backlog** : les 29 points de l'audit initial sont maintenant tous
traités (4 critiques + 14 majeurs + 11 mineurs), sauf l'observation
`mqtt_broker` notée ci-dessus si l'utilisateur souhaite l'inclure.

---

## [2026-08-21] Correction mqtt_broker (même défaut que P28)

Sur demande explicite, application du même correctif que P28 à
`mqtt_broker` : défaut passé de `"192.168.1.10"` à `""` dans
`config.yaml`. Même raisonnement — schema `str` (obligatoire) + validation
bashio (`[ -z "${MQTT_BROKER}" ]` dans le script `run`) ne pouvaient pas
se déclencher tant qu'une IP plausible était pré-remplie.

**Vérification** : `py_compile` (fichier Python non touché, inchangé) ;
grep confirmant que les mentions de `192.168.1.10` restantes dans la
documentation sont des exemples illustratifs ("ex: 192.168.1.10"), pas des
affirmations sur la valeur par défaut réelle — cohérent avec le traitement
déjà fait pour `tv_ip`/`192.168.1.100` en P28.

**Aucun impact** sur le code Python ni sur les corrections précédentes
(P1-P29) : changement isolé à `config.yaml`.
