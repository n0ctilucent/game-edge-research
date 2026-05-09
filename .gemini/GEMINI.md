# ASUS Tinker Edge T - Skynet Tier 2 Node Documentation

**Project:** bitsmasher.net Decentralized Edge AI Network ("Skynet")  
**Hardware:** ASUS Tinker Edge T (i.MX 8MQ + Coral Edge TPU)  
**OS:** Mendel GNU/Linux 5 (Eagle) aarch64  
**Status:** 🟢 ONLINE / DEPLOYED  

---

## Overview

The Skynet Tier 2 Node is a decentralized edge AI system operating on the [ASUS Tinker Edge T](https://tinker-board.asus.com/product/tinker-edge-t.html) board. This documentation details the node's architecture, hardware capabilities, system optimizations, and operational services. The primary goal of this node is to act as a local "brain" that ingests raw environmental data (video), performs heavy matrix mathematics locally using LiteRT, and transmits only lightweight intelligence (JSON telemetry) back to the Core server.

---

## 1. Architecture

The node fits into the broader bitsmasher.net network hierarchy:

* **Tier 1 (The Core):** `chonk` (10.10.8.60) & `stargate`. Handles data aggregation, [Mosquitto MQTT](https://mosquitto.org/) routing, game server hosting (RCON), and long-term storage via NFS.
* **Tier 2 (Tactical Edge):** `edge-t`. Runs [LiteRT](https://ai.google.dev/edge/litert) (formerly TensorFlow Lite) headless object detection at 4 TOPS using 0.5W.
* **Tier 3 (Senses & Actuators):** 1080p Logitech webcams, MIPI-CSI modules, and ESP32/ESP8266 IoT badges.

---

## 2. Hardware Specifications

* **Compute:** NXP i.MX 8M Quad-core Arm Cortex-A53 (1.5GHz).
* **Accelerator:** Internal [Google Coral Edge TPU](https://coral.ai/) (`/dev/apex_0`) over PCIe (Verified at 5GT/s, Width x1).
* **Power & Thermals:** Custom 45W power design with active heatsink. CPU throttles at 80°C.

---

## 3. System Optimizations

To ensure zero CLI latency and maximum resources for the Edge TPU, the following "Cold & Small" profile optimizations are permanently applied:

* **CPU Governor:** Locked to `performance` mode to prevent downclocking.
* **Network Latency:** IPv6 disabled globally via `sysctl` to speed up SSH and internal routing.
* **Background Noise:** Mendel development services (`avahi-daemon`, `mdt-keymaster`) masked.
* **Shell Speed:** Programmable `bash-completion` disabled in `~/.bashrc` to prevent eMMC/NFS crawling delays during autocomplete.
* **Vision Dependencies:** Standard `python3-opencv` APT packages purged to avoid GUI bloat. Installed `opencv-python-headless` via `pip` to ensure a pure server-side video pipeline.

---

## 4. The Skynet Vision Service

The board runs a persistent `systemd` daemon that captures video, detects objects, and streams telemetry over the lab network.

### A. The Payload
* **Model:** SSD MobileNet V2 (COCO Quantized for Edge TPU).
* **Detection Threshold:** Configured for >60% confidence.

### B. The Uplink (MQTT)
Telemetry is formatted as lightweight JSON and published to the Tier 1 Core.
* **Broker:** `10.10.8.60` (`chonk`) on Port `1883`.
* **Topic:** `skynet/tier2/edge-t/vision`
* **Sample Output:** ```json
    {"node": "edge-t", "timestamp": 1778348536.623, "detections": [{"class": "person", "confidence": 87.1}, {"class": "tv", "confidence": 61.7}]}
    ```

---

## 5. Testing and Validation

The hardware and software stack were validated using standardized Coral models to ensure native PCIe delegation to the Edge TPU:

* **Image Classification Benchmark:** `mobilenet_v2_1.0_224_quant` executes natively on the TPU in **~2.89ms**.
* **Live Video Pipeline Benchmark:** `ssd_mobilenet_v2_coco_quant` coupled with [OpenCV](https://opencv.org/) headless frame ingestion executes at **~15 FPS (66.7ms per frame)** on a live 1080p USB webcam feed.

---

## 6. Management and Troubleshooting

### Service Management
The vision service auto-restarts on failure. It can be managed with standard `systemctl` commands:

* **View real-time AI detections & logs:** `journalctl -u skynet-vision.service -f`
* **Restart the camera pipeline:** `sudo systemctl restart skynet-vision.service`
* **Check service status:** `systemctl status skynet-vision.service`

### Known Issues & Fixes

* **Connection Refused (Errno 111):** If the service logs show MQTT connection refusals, ensure the Mosquitto broker on `chonk` has `listener 1883 0.0.0.0` configured in `/etc/mosquitto/conf.d/skynet.conf` and that `ufw allow 1883/tcp` is open.
* **Vim Stair-Stepping:** When editing Python scripts on the headless node, always use `:set paste` in `vi` before pasting code to prevent whitespace indentation errors.
* **Laggy Autocomplete:** Ensure NFS mounts (`/mnt/clusterfs`) are active. Network jitter on broken network paths will cause the shell to hang.

---

## 7. Future Development

With the foundation verified, next steps for the bitsmasher.net lab include:

* **Database Ingestion:** Configure a listener on `chonk` to parse the MQTT JSON and log timestamps/classes to a SQL database for historical analysis.
* **IoT Actuation:** Flash lab ESP32 badges to subscribe to the MQTT topic and trigger NeoPixels/relays based on specific detections (e.g., flash red when `class: person` is detected).
* **Game Server Synergy:** Build a Python bridge on `chonk` that reads the physical MQTT telemetry and leverages RCON to broadcast in-game alerts (e.g., triggering a `/broadcast "Physical movement detected!"` in Minecraft when someone enters the lab).
