# modpoll2mqtt — Passerelle Modbus vers MQTT

[![Release](https://img.shields.io/github/v/release/yoch/modpoll2mqtt)](https://github.com/yoch/modpoll2mqtt/releases)
[![Build status](https://img.shields.io/github/actions/workflow/status/yoch/modpoll2mqtt/main.yml?branch=main)](https://github.com/yoch/modpoll2mqtt/actions/workflows/main.yml?query=branch%3Amain)
[![License](https://img.shields.io/github/license/yoch/modpoll2mqtt)](https://github.com/yoch/modpoll2mqtt/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/modpoll2mqtt/week)](https://pepy.tech/project/modpoll2mqtt)

> Documentation : [yoch.github.io/modpoll2mqtt](https://yoch.github.io/modpoll2mqtt)

**modpoll2mqtt** est une passerelle Modbus → MQTT en ligne de commande. Elle interroge des équipements Modbus (RTU, TCP, UDP) selon un fichier CSV de configuration, publie les valeurs sur un broker MQTT et accepte des commandes d’écriture par référence.

Le package s’installe sous le nom PyPI `modpoll2mqtt` ; la commande exécutable reste `modpoll`.

Fork de [modpoll](https://github.com/gavinying/modpoll), avec notamment l’écriture MQTT sémantique par `ref` + `value` et des exemples CTA (centrales de traitement d’air).

## Fonctionnalités

- Modbus RTU, TCP et UDP (fichiers CSV de configuration)
- Affichage local des données pollées (mode debug)
- Publication MQTT des références (topics configurables)
- Écriture MQTT par nom de référence CSV (`modpoll/<device>/set`)
- Export CSV local des données
- Accès bit à bit sur registres et coils

## Installation

Python 3.10+ requis.

```bash
pip install modpoll2mqtt
```

Option Modbus série (pyserial) :

```bash
pip install 'modpoll2mqtt[serial]'
```

Mise à jour :

```bash
pip install -U modpoll2mqtt
```

Sous Windows, [pipx](https://pypa.github.io/pipx/installation/) est recommandé :

```powershell
pipx install modpoll2mqtt
```

## Quickstart

Lecture unique d’un équipement Modbus TCP (remplacer l’adresse IP par la vôtre) :

```bash
modpoll --once \
  --tcp 192.168.1.10 \
  --config examples/modsim.csv
```

Publication vers un broker MQTT :

```bash
modpoll \
  --tcp 192.168.1.10 \
  --mqtt-host broker.emqx.io \
  --config examples/modsim.csv
```

Les données sont publiées sur `modpoll/<device_name>/data` par défaut.

### Écriture par référence MQTT

Une fois connecté au broker, `modpoll` s’abonne à `modpoll/+/set`. Publier sur `modpoll/<device>/set` :

```json
{
  "ref": "PID_V3V_EC_Consigne_reprise",
  "value": 21.5
}
```

Exemple avec [`examples/CTA/cta_conf_restaurant.csv`](examples/CTA/cta_conf_restaurant.csv) : une référence `int16` avec échelle `0.1` accepte `21.5` en entrée ; la valeur brute `215` est écrite dans le registre.

**Migration depuis modpoll 1.6.x :** le format bas niveau (`object_type`, `address`, `value`) n’est plus supporté.

### Pièges de configuration

- Sur les pollers **coil** / **discrete_input**, utiliser `bool` avec l’**adresse Modbus absolue** pour un seul booléen.
- `bool8` / `bool16` : lectures groupées legacy (index de groupe, pas adresse coil directe).
- Sur **holding_register** / **input_register**, `bool` avec `adresse:bit` (0–15), ex. `40019:15,bool`.
- `<endian>` : `BE_BE`, `LE_BE`, `LE_LE` ou `BE_LE` uniquement.
- `--autoremove` : désactive un poller après 3 échecs Modbus consécutifs.

## Exemples

```bash
# Modbus TCP
modpoll --tcp 192.168.1.10 --config examples/modsim.csv

# Modbus série
modpoll --serial /dev/ttyUSB0 --serial-baud 9600 --config contrib/eniwise/scpms6.csv

# MQTT + export CSV
modpoll --tcp 192.168.1.10 --mqtt-host localhost --export data.csv --config examples/modsim.csv

# Plusieurs fichiers de config
modpoll --tcp 192.168.1.10 --config examples/modsim.csv examples/modsim2.csv

# CTA (exemple métier)
modpoll --tcp 192.168.1.20 --mqtt-host localhost --config examples/CTA/cta_conf_restaurant.csv
```

Voir le dossier [`examples/`](examples/) et [`contrib/`](contrib/) pour d’autres configurations.

## Credits

Ce projet s’appuie sur :

- [modpoll](https://github.com/gavinying/modpoll) — Ying Shaodong (MIT)
- [modbus2mqtt](https://github.com/owagner/modbus2mqtt) — Oliver Wagner (MIT)
- [spicierModbus2mqtt](https://github.com/mbs38/spicierModbus2mqtt) — Max Brueggemann (MIT)

## Licence

MIT — voir [LICENSE](LICENSE).
