# ASUS Tinker Edge T - Lab Reference & Optimization Guide
**Project:** bitsmasher.net Edge AI Deployment
**Hardware:** ASUS Tinker Edge T (i.MX 8MQ + Coral Edge TPU)
[cite_start]**OS:** Mendel GNU/Linux 5 (Eagle) aarch64 [cite: 742]

---

## 1. Hardware Specifications
The Tinker Edge T is engineered for "cold and small" local AI inference, providing a robust architecture for sustained edge operations.

* [cite_start]**CPU:** NXP i.MX 8M Quad-core Arm Cortex-A53 (1.5GHz) with a Cortex-M4F real-time core[cite: 912, 1337].
* [cite_start]**Accelerator:** Internal Google Edge TPU over PCIe, capable of 4 TOPS at 0.5W per unit of computation[cite: 911, 1334].
* [cite_start]**Memory/Storage:** 1GB LPDDR4 RAM and 8GB onboard eMMC[cite: 912, 1338].
* [cite_start]**Thermals:** Active heatsink included to prevent the CPU from throttling, which occurs at 80°C[cite: 914, 1366].
* [cite_start]**Power Delivery:** Custom 45W power design (12~19v DC) ensures full I/O performance and stability, overcoming the limits of standard 15W SBCs[cite: 913, 1361].

---

## 2. Software & Ecosystem Shift
* [cite_start]**Runtime Framework:** Google has transitioned the traditional TensorFlow Lite ecosystem to **LiteRT**, serving as the unified framework for high-performance, on-device machine learning and GenAI deployments[cite: 724, 1427].
* [cite_start]**Operating System:** Runs Mendel Linux, a lightweight derivative of Debian specifically optimized for the Coral/Edge TPU ecosystem[cite: 750, 1340].

---

## 3. Lab Optimization Profile
By default, the Mendel OS favors power-saving and background discovery tasks. To eliminate CLI latency and optimize the board for direct SSH management, the following configuration baseline was established:

### System & Network
* [cite_start]**CPU Governor:** Set permanently to `performance` to keep the CPU locked at 1.5GHz, eliminating keystroke ramp-up lag[cite: 915].
* [cite_start]**IPv6 Disabled:** `net.ipv6.conf.all.disable_ipv6=1` applied via `sysctl` to speed up SSH handshakes and network polling[cite: 851, 916].
* [cite_start]**Background Services:** Masked `avahi-daemon` (mDNS) and `mdt-keymaster` (Mendel Development Tool) to stop background polling and CPU interrupts[cite: 782, 916].

### Shell Responsiveness
* **Autocomplete Stalls:** The default `bash-completion` script crawls `/usr/bin` and mounted network paths upon hitting `TAB`. [cite_start]Commenting this out in `~/.bashrc` ensures instant autocomplete[cite: 868, 917].
* [cite_start]**NFS Warning:** Mounting `chonk` and `stargate` via NFS creates shell latency if network jitter occurs during path resolution[cite: 901, 918]. 

---

## 4. Hardware Verification Scripts

### A. Edge TPU Device Link
The Edge TPU is connected via PCIe and utilizes the `apex` driver group.
* [cite_start]**Device Node:** `/dev/apex_0`[cite: 749].
* [cite_start]**PCIe Bus Speed:** Verified at `Speed 5GT/s, Width x1` via `lspci -d 1ac1:089a -vvv`[cite: 797, 842].

### B. System Health Diagnostic (`edge_t_diag.sh`)
[cite_start]Since standard packages like `bc` and `zram-config` are stripped from the minimal Mendel image [cite: 821, 848][cite_start], this script uses `awk` for floating-point math to monitor thermals and hardware links[cite: 823, 850].

```bash
#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}--- [ CPU & Thermals ] ---${NC}"
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
TEMP_C=$(awk "BEGIN {print $TEMP/1000}")
echo "Governor: $GOV"
echo "Temp:     ${TEMP_C}°C"

echo -e "\n${GREEN}--- [ Edge TPU (Apex) Status ] ---${NC}"
if [ -e /dev/apex_0 ]; then
    LNK=$(sudo lspci -vv -s 0001:01:00.0 | grep "LnkSta:" | awk '{print $2, $3}')
    echo -e "Device Node: ${GREEN}/dev/apex_0 detected${NC}"
    echo "PCI Link:    $LNK"
else
    echo -e "Device Node: ${RED}NOT FOUND${NC}"
fi
