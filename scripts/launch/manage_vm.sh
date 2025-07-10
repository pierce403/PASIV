#!/bin/bash
# PASIV VM Manager - Libvirt Edition
# Manages the ubuntu-desktop-vulnerable VM through libvirt

VM_NAME="ubuntu-desktop-vulnerable"
SHARED_MEMORY_PATH="/dev/shm/pasiv_vulnerable_memory"

show_usage() {
    echo "Usage: $0 {start|stop|restart|status|console|info|gui}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the VM"
    echo "  stop     - Gracefully shutdown the VM"
    echo "  restart  - Restart the VM"
    echo "  status   - Show VM status"
    echo "  console  - Connect to VM console (text mode)"
    echo "  info     - Show detailed VM information"
    echo "  gui      - Open virt-manager GUI"
    echo ""
    echo "Note: The VM uses shared memory at $SHARED_MEMORY_PATH"
}

check_vm_exists() {
    if ! virsh list --all | grep -q "$VM_NAME"; then
        echo "Error: VM '$VM_NAME' not found!"
        echo "Run 'virsh list --all' to see available VMs"
        exit 1
    fi
}

setup_shared_memory() {
    if [ ! -f "$SHARED_MEMORY_PATH" ]; then
        echo "Setting up shared memory for DMA attacks..."
        sudo mkdir -p "$(dirname "$SHARED_MEMORY_PATH")"
        # Create 4GB shared memory file
        sudo fallocate -l 4G "$SHARED_MEMORY_PATH" 2>/dev/null || \
        sudo dd if=/dev/zero of="$SHARED_MEMORY_PATH" bs=1M count=4096 status=progress
        sudo chmod 666 "$SHARED_MEMORY_PATH"
        echo "Shared memory ready at $SHARED_MEMORY_PATH"
    fi
}

start_vm() {
    echo "Starting VM: $VM_NAME"
    setup_shared_memory
    virsh start "$VM_NAME"
    if [ $? -eq 0 ]; then
        echo "VM started successfully!"
        echo "You can:"
        echo "  - Open virt-manager GUI: $0 gui"
        echo "  - Connect to console: $0 console"
        echo "  - Check status: $0 status"
    fi
}

stop_vm() {
    echo "Stopping VM: $VM_NAME"
    virsh shutdown "$VM_NAME"
    echo "Shutdown signal sent. VM will gracefully shut down."
}

restart_vm() {
    echo "Restarting VM: $VM_NAME"
    virsh reboot "$VM_NAME"
}

force_stop_vm() {
    echo "Force stopping VM: $VM_NAME"
    virsh destroy "$VM_NAME"
    echo "VM forcefully stopped."
}

vm_status() {
    echo "=== VM Status ==="
    virsh list --all | grep "$VM_NAME"
    echo ""
    echo "=== Shared Memory ==="
    if [ -f "$SHARED_MEMORY_PATH" ]; then
        ls -lh "$SHARED_MEMORY_PATH"
    else
        echo "Shared memory not set up yet"
    fi
}

vm_info() {
    echo "=== VM Information ==="
    virsh dominfo "$VM_NAME"
    echo ""
    echo "=== VM Configuration ==="
    virsh dumpxml "$VM_NAME" | head -20
}

connect_console() {
    echo "Connecting to VM console..."
    echo "Press Ctrl+] to disconnect"
    virsh console "$VM_NAME"
}

open_gui() {
    echo "Opening virt-manager GUI..."
    virt-manager --connect qemu:///system --show-domain-console "$VM_NAME" &
}

# Main script
case "$1" in
    start)
        check_vm_exists
        start_vm
        ;;
    stop)
        check_vm_exists
        stop_vm
        ;;
    force-stop)
        check_vm_exists
        force_stop_vm
        ;;
    restart)
        check_vm_exists
        restart_vm
        ;;
    status)
        check_vm_exists
        vm_status
        ;;
    console)
        check_vm_exists
        connect_console
        ;;
    info)
        check_vm_exists
        vm_info
        ;;
    gui)
        open_gui
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 