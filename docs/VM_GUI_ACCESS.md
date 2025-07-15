# PASIV VM GUI Access

## Current Setup
The PASIV VM runs with SPICE display (not headless) for full GUI access during DMA attacks.

## GUI Connection
**SPICE Display**: Port 5901
```bash
# Primary method (recommended)
remote-viewer spice://localhost:5901

# Alternative viewer
virt-viewer spice://localhost:5901
```

## Quick Launch
```bash
# Start VM with file-backed memory
./src/vm/file_backed_memory_vm.sh

# Connect to GUI
remote-viewer spice://localhost:5901 &
```

## VM Details
- **Display**: SPICE on localhost:5901
- **SSH**: localhost:2222  
- **Memory**: Direct file access via `./pasiv_vm_memory.img`
- **OS**: Ubuntu Desktop (vulnerable target)

## Required Packages
```bash
sudo apt install virt-viewer  # Provides remote-viewer and virt-viewer
```

## Notes
- SPICE provides better performance than VNC
- GUI access needed for visual verification of DMA attacks
- VM runs with file-backed memory for direct DMA simulation
- Display is bound to localhost (secure) 