# Target Configurations

This directory contains configuration files and templates for setting up various virtual machine targets for DMA attack testing.

## Purpose

Standardize VM configurations across different operating systems and security postures, ensuring reproducible testing environments for DMA attack research.

## Planned Configuration Files

### Operating System Configurations
- [ ] **ubuntu_server_vulnerable.xml** - Ubuntu Server with minimal protections
- [ ] **ubuntu_server_hardened.xml** - Ubuntu Server with IOMMU enabled
- [ ] **windows10_vulnerable.xml** - Windows 10 test target
- [ ] **windows10_hardened.xml** - Windows 10 with security features
- [ ] **debian_minimal.xml** - Lightweight Debian testing environment

### QEMU Launch Configurations
- [ ] **vulnerable_target.conf** - Standard vulnerable VM parameters
- [ ] **hardened_target.conf** - IOMMU-protected VM parameters
- [ ] **research_target.conf** - Custom research environment settings

### Guest OS Configurations
- [ ] **disable_kaslr.conf** - Kernel parameters for reproducible testing
- [ ] **enable_iommu.conf** - IOMMU activation parameters
- [ ] **debug_settings.conf** - Enhanced logging and debugging options

### Network Configurations
- [ ] **isolated_network.xml** - Isolated testing network
- [ ] **port_forwarding.conf** - SSH and service access configuration
- [ ] **monitoring_network.xml** - Network with traffic analysis capabilities

## Configuration Structure

### VM Hardware Specifications
- Memory allocation (typically 2-4GB for testing)
- CPU core assignment with virtualization features
- Storage configuration (qcow2 disk images)
- Network interface setup

### Security Postures

**Vulnerable Targets:**
- Shared memory enabled (/dev/shm backing)
- KASLR disabled for consistent memory layout
- Minimal security features enabled
- Direct hardware access permitted

**Hardened Targets:**
- Virtual IOMMU protection enabled
- Memory protection mechanisms active
- Security features maximized
- Limited hardware access

### Automation Integration
- Compatible with libvirt management
- Templated for easy customization
- Environment variable substitution
- Validation scripts included

## Usage

Configuration files can be used with:
- `virsh create <config.xml>` for libvirt
- `qemu-system-x86_64 @<config.conf>` for direct QEMU
- Custom launch scripts in `/scripts/launch/`

## Template Variables

Common template variables include:
- `${VM_NAME}` - Unique identifier for the VM instance
- `${MEMORY_SIZE}` - RAM allocation in MB
- `${DISK_IMAGE}` - Path to the VM disk image
- `${SHARED_MEMORY}` - Path to shared memory object 