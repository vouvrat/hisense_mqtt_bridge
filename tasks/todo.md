# Todo

## Terminé — Correction des 11 mineurs (2026-08-21)

Détail complet, analyse de risque et corrections dans tasks/historique.md.

- [x] P19 : imports morts retirés (hashlib, socket)
- [x] P20 : validation claire des int() dans load_config()
- [x] P21 : logs DEBUG tronqués (2 endroits)
- [x] P22 : commentaire justificatif TLS CERT_NONE
- [x] P23 : typage volume TV (coercition int + warning)
- [x] P24 : python3/py3-pip retirés du Dockerfile (vérifié redondant via
  Dockerfile source officiel home-assistant/docker-base)
- [x] P25 : mosquitto-clients/jq retirés du Dockerfile (inutilisés)
- [x] P26 : URL placeholder + fausse liste d'entités corrigées dans
  HOME_ASSISTANT.md et CONFIGURATION.md (même défaut que P14, découvert
  non traité dans ces 2 fichiers) + incohérence ADDON_READY.md corrigée
- [x] P27 : commentaire sur l'épinglage paho-mqtt 1.6.1
- [x] P28 : tv_ip par défaut vide (validation "obligatoire" réelle)
- [x] P29 : plus de dates/URL obsolètes (vérifié par grep exhaustif)

**Vérifié** : py_compile, relecture complète run()/stop()/main() après le
lot — P1-P18 confirmés intacts. Recherche exhaustive de références mortes.
**Non vérifié** : build Docker réel, connexion TV/MQTT réelle (aucun
matériel/broker disponible ici) — à valider en déploiement HA réel.

## État du projet

Les 29 points de l'audit initial (tasks/historique.md, entrée du
2026-08-21) sont maintenant tous traités : 4 critiques + 14 majeurs +
11 mineurs.

**Observation non traitée (hors périmètre P28)** : `mqtt_broker` a le même
défaut "IP plausible qui contourne la validation obligatoire" que `tv_ip`
avait — à corriger si l'utilisateur le souhaite dans une prochaine passe.

**Prochaine étape naturelle** : déploiement réel sur une instance Home
Assistant pour valider ce qui ne peut pas l'être dans cet environnement
(build Docker, connexion TV/MQTT réelle).
