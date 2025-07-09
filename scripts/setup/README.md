# Setup Scripts

This directory contains automation scripts for setting up the PASIV testing environment.

## Purpose

Automate the installation and configuration of all dependencies required for DMA attack testing, including QEMU/KVM, virtualization tools, and memory forensics frameworks.

## Planned Scripts

### Core Dependencies
- [ ] **install_deps.sh** - Install QEMU/KVM, libvirt, virt-manager, build tools
- [ ] **setup_virtualization.sh** - Configure hardware virtualization support
- [ ] **user_permissions.sh** - Add user to required groups (kvm, libvirt)

### Guest Image Management
- [ ] **create_guest_image.sh** - Download OS ISOs and create VM disk images
- [ ] **configure_vulnerable_guest.sh** - Setup vulnerable target configurations
- [ ] **configure_hardened_guest.sh** - Setup IOMMU-protected targets

### Tool Installation
- [ ] **install_pcileech.sh** - Build and install PCILeech framework
- [ ] **install_memprocfs.sh** - Setup MemProcFS for memory analysis
- [ ] **install_memflow.sh** - Install Rust-based memflow connectors

## Usage

All scripts should be run from the project root with appropriate permissions. See individual script documentation for specific requirements. 