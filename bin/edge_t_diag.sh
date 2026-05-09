#!/bin/bash
# edge_t_diag.sh - Tinker Edge T Health & Performance Triage
# 2026 Lab Standard for bitsmasher.net

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}--- [ System Baseline ] ---${NC}"
echo "Hostname: $(hostname)"
echo "Kernel:   $(uname -r)"
echo "Uptime:  $(uptime -p)"

echo -e "\n${GREEN}--- [ CPU & Thermals ] ---${NC}"
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
echo "Governor: $GOV"
#echo "Temp:     $(echo "scale=2; $TEMP/1000" | bc)°C"
echo "Temp:     $(awk "BEGIN {print $TEMP/1000}")°C"

echo -e "\n${GREEN}--- [ Edge TPU (Apex) Status ] ---${NC}"
if [ -e /dev/apex_0 ]; then
	    echo -e "Device Node: ${GREEN}/dev/apex_0 detected${NC}"
	        # Checking PCI link status for the Edge TPU
		    lspci -d 1ac1:089a -vv | grep -i "LnkSta:" || echo "PCI Info: Use sudo for detailed link status."
	    else
		        echo -e "Device Node: ${RED}NOT FOUND${NC}"
fi

echo -e "\n${GREEN}--- [ Memory & I/O ] ---${NC}"
free -h | grep "Mem:"
vmstat 1 2 | tail -n 1 | awk '{print "CPU I/O Wait: "$16"%"}'

echo -e "\n${GREEN}--- [ Latency Culprits ] ---${NC}"
for svc in avahi-daemon mdt-keymaster; do
	    STATUS=$(systemctl is-active $svc)
	        if [ "$STATUS" == "active" ]; then
			        echo -e "$svc: ${RED}Running${NC}"
				    else
					            echo -e "$svc: ${GREEN}Stopped${NC}"
						        fi
						done

						echo -e "\n${GREEN}--- [ SSH Optimization ] ---${NC}"
						grep -E "UseDNS|GSSAPIAuthentication" /etc/ssh/sshd_config | grep "no" > /dev/null
						if [ $? -eq 0 ]; then
							    echo -e "SSH Config: ${GREEN}Optimized${NC}"
						    else
							        echo -e "SSH Config: ${RED}Standard (Potentially Laggy)${NC}"
						fi
