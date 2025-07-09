# VM Launch Scripts

This directory contains scripts for launching different types of virtual machine targets for DMA attack testing.

## Purpose

Provide standardized launch configurations for vulnerable and hardened virtual machines with appropriate memory sharing, IOMMU settings, and monitoring capabilities.

## Planned Scripts

### Target Configurations
- [ ] **launch_vulnerable_guest.sh** - Launch VM with shared memory, no IOMMU protection
- [ ] **launch_hardened_guest.sh** - Launch VM with virtual IOMMU enabled
- [ ] **launch_custom_guest.sh** - Configurable launcher with custom parameters

### Memory Management
- [ ] **setup_shared_memory.sh** - Configure /dev/shm file-backed memory objects
- [ ] **mount_memprocfs.sh** - Mount guest memory using MemProcFS
- [ ] **unmount_memprocfs.sh** - Clean shutdown and unmount procedures

### Monitoring & Control
- [ ] **expose_qmp_socket.sh** - Enable QMP socket for advanced introspection
- [ ] **setup_port_forwarding.sh** - Configure SSH and service access
- [ ] **vm_status.sh** - Check running VM status and connections

## VM Configurations

### Vulnerable Target Features
- File-backed shared memory in /dev/shm
- KASLR disabled (nokaslr kernel parameter)
- Direct memory access enabled
- Port forwarding for SSH access

### Hardened Target Features
- Virtual IOMMU protection (-device intel-iommu)
- IOMMU kernel parameters (intel_iommu=on)
- Memory protection enabled
- Attack surface minimization

## Usage

Launch scripts should be executed with appropriate privileges. Ensure host system has virtualization enabled and required dependencies installed. 