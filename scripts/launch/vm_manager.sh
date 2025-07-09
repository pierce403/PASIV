#!/bin/bash

# PASIV - VM Manager
# Simple script to manage PASIV virtual machines

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_usage() {
    echo "PASIV VM Manager"
    echo "==============="
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start        Start the vulnerable Ubuntu Desktop VM"
    echo "  stop         Stop all PASIV VMs"
    echo "  status       Show status of running VMs"
    echo "  download     Check Ubuntu ISO download progress"
    echo "  connect      Connect to VM via VNC"
    echo "  ssh          SSH to the VM (once installed)"
    echo "  help         Show this help message"
    echo ""
}

start_vm() {
    echo -e "${GREEN}Starting PASIV Vulnerable Desktop VM...${NC}"
    if [ ! -f "scripts/launch/launch_vulnerable_desktop.sh" ]; then
        echo -e "${RED}Error: Launch script not found. Run from PASIV project root.${NC}"
        exit 1
    fi
    
    ./scripts/launch/launch_vulnerable_desktop.sh
}

stop_vms() {
    echo -e "${YELLOW}Stopping all PASIV VMs...${NC}"
    
    # Kill QEMU processes with PASIV VM names
    if pgrep -f "qemu.*ubuntu.*vulnerable" > /dev/null; then
        pkill -f "qemu.*ubuntu.*vulnerable"
        echo -e "${GREEN}Stopped vulnerable desktop VM${NC}"
    else
        echo "No PASIV VMs found running"
    fi
    
    # Clean up shared memory files
    if [ -f "/dev/shm/pasiv_vulnerable_memory" ]; then
        rm -f "/dev/shm/pasiv_vulnerable_memory"
        echo "Cleaned up shared memory files"
    fi
    
    # Clean up QMP sockets
    rm -f /tmp/pasiv_*_qmp.sock
    echo "Cleaned up QMP sockets"
}

show_status() {
    echo "PASIV VM Status"
    echo "==============="
    echo ""
    
    # Check for running VMs
    if pgrep -f "qemu.*ubuntu.*vulnerable" > /dev/null; then
        echo -e "${GREEN}✓ Vulnerable Desktop VM: RUNNING${NC}"
        
        # Show connection info
        echo "  VNC: localhost:5901"
        echo "  SSH: ssh -p 2222 username@localhost"
        echo "  QMP: /tmp/pasiv_vulnerable_qmp.sock"
        
        # Check shared memory
        if [ -f "/dev/shm/pasiv_vulnerable_memory" ]; then
            MEMORY_SIZE=$(ls -lh /dev/shm/pasiv_vulnerable_memory | awk '{print $5}')
            echo "  Shared Memory: /dev/shm/pasiv_vulnerable_memory ($MEMORY_SIZE)"
        fi
    else
        echo -e "${RED}✗ No PASIV VMs running${NC}"
    fi
    
    echo ""
    
    # Check ISO download
    if [ -f "iso_files/ubuntu-22.04.5-desktop-amd64.iso" ]; then
        echo -e "${GREEN}✓ Ubuntu Desktop ISO: Available${NC}"
    else
        if pgrep -f "wget.*ubuntu.*iso" > /dev/null; then
            echo -e "${YELLOW}⏳ Ubuntu Desktop ISO: Downloading...${NC}"
        else
            echo -e "${RED}✗ Ubuntu Desktop ISO: Not found${NC}"
        fi
    fi
}

connect_vnc() {
    echo -e "${GREEN}Connecting to VM via VNC...${NC}"
    echo "VNC Address: localhost:5901"
    echo ""
    echo "Use a VNC client to connect, or try:"
    echo "  vncviewer localhost:5901"
    echo "  remmina vnc://localhost:5901"
    echo ""
    echo "If no VNC client is installed:"
    echo "  sudo apt install tigervnc-viewer"
}

ssh_vm() {
    echo -e "${GREEN}SSH Connection Info:${NC}"
    echo "  ssh -p 2222 username@localhost"
    echo ""
    echo "Note: SSH is only available after Ubuntu installation is complete"
    echo "and a user account has been configured."
}

case "$1" in
    start)
        start_vm
        ;;
    stop)
        stop_vms
        ;;
    status)
        show_status
        ;;
    download)
        ./scripts/launch/check_iso_download.sh
        ;;
    connect|vnc)
        connect_vnc
        ;;
    ssh)
        ssh_vm
        ;;
    help|--help|-h)
        show_usage
        ;;
    "")
        show_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac 