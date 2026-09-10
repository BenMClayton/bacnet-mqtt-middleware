# BACnet MQTT Middleware

A small integration prototype for discovering BACnet/IP devices while
monitoring MQTT telemetry. It is aimed at local building-automation labs where
BACnet equipment and Zigbee2MQTT share an integration host.

## Features

- broadcasts BACnet `Who-Is` and handles `I-Am` responses;
- reads names, descriptions, units, and present values from discovered objects;
- connects to a configurable MQTT broker and topic filter; and
- includes a Python BACnet thermostat simulator for local experimentation.

## Quick start

Requirements: Node.js 18+ and access to an MQTT broker.

```sh
npm ci
cp .env.example .env
npm start
```

The Node process reads configuration from the environment. Load `.env` with
your preferred process manager or export the variables in your shell before
running it.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MQTT_URL` | `mqtt://localhost:1883` | MQTT broker URL |
| `MQTT_TOPIC` | `zigbee2mqtt/#` | Subscription filter |
| `BACNET_INTERFACE` | automatic | Local BACnet/IP interface |
| `BACNET_APDU_TIMEOUT` | `10000` | BACnet request timeout in milliseconds |

## BACnet simulator

The simulator is intentionally separate from the Node process:

```sh
python -m venv .venv
python -m pip install -r bacnet-simulator/requirements.txt
python bacnet-simulator/device-sim.py --ip 0.0.0.0 --port 47808
```

It provides two changing thermostat values and a small setpoint GUI. BACnet/IP
uses UDP broadcast, so container, firewall, and subnet settings may need to be
adjusted for your lab.

## Scope and safety

This is a demonstrator, not a production gateway. It performs discovery and
read-only BACnet property access; it does not authenticate MQTT connections or
write BACnet values. Use it only on networks you are authorised to test, and
provide broker authentication through your deployment environment when needed.

## Verification

```sh
npm run check
python -m py_compile bacnet-simulator/device-sim.py
```
