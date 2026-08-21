# Lessons

Format : [date] | ce qui a mal tourné | règle pour l'éviter

[2026-08-21] | En corrigeant les dépendances Python mortes (Dockerfile), j'ai aussi supprimé `python3`/`py3-pip`/`mosquitto-clients`/`jq` de l'`apk add` sans que ce soit demandé ni vérifiable sans build Docker réel. | Ne jamais bundler un nettoyage hors-périmètre avec un fix demandé, même trivial en apparence — traiter chaque point de l'audit un par un, strictement dans le périmètre validé.

[2026-08-21] | L'audit initial supposait qu'un simple changement de tag Alpine suffirait à corriger l'image de base obsolète (P16). En vérifiant via l'API GHCR avant d'agir, découvert que cette image était gelée depuis fin 2024 sans tag plus récent disponible. | Toujours interroger la source de vérité (registre, API, dépôt source) avant de changer une référence d'image/dépendance dans un Dockerfile — ne jamais deviner qu'un tag existe.

[2026-08-21] | En augmentant le timeout de `setup_tv()` (10s→35s) pour corriger un bug de délai de connexion TV, j'ai failli introduire une régression silencieuse : le thread de monitoring bloquait dans ce timeout sans vérifier une demande d'arrêt, retardant `stop()` jusqu'à 35s. | Après avoir changé une durée/timeout dans une boucle d'attente, toujours vérifier son effet sur les chemins d'arrêt/annulation, pas seulement le chemin nominal — et le dire explicitement si ça a nécessité une correction en cours de route.
