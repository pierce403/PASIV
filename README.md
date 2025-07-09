# PASIV: Programmable Automated Security Interrogation for Virtualization

PASIV is a comprehensive test harness for emulating, executing, and analyzing Direct Memory Access (DMA) attacks within a controlled QEMU/KVM environment. This framework aims to provide researchers and security professionals with a powerful, scriptable, and repeatable platform for studying DMA vulnerabilities and defenses.

## Project Goals

- Automate the setup of vulnerable and hardened virtual machine targets.
- Integrate with leading memory forensics tools like PCILeech, memflow, and MemProcFS.
- Provide a modular framework for developing and executing custom DMA attack payloads.
- Enable the study and verification of IOMMU-based defenses.
- Serve as a research platform for advanced DMA attack and defense techniques.

## Development Roadmap & To-Do List

This is a living document tracking the features and milestones for the PASIV framework.

### Phase 1: Core Environment & Automation (/scripts)

**[ ] Host Setup Script (/scripts/setup/install_deps.sh):**
- Automate installation of QEMU/KVM, libvirt, virt-manager, and other required host packages (e.g., build-essential).
- Check for and guide the user on enabling hardware virtualization (VT-x/AMD-V) in BIOS/UEFI.
- Add the current user to kvm and libvirt groups.

**[ ] Guest Image Creation (/scripts/setup/create_guest_image.sh):**
- Script to download a specified OS ISO (e.g., Ubuntu Server LTS).
- Use qemu-img to create a .qcow2 disk image for the guest.
- (Stretch Goal) Automate the OS installation process using preseed/autoinstall configurations.

**[ ] VM Launch Scripts (/scripts/launch/):**

*Vulnerable Target (launch_vulnerable_guest.sh):*
- Launch QEMU guest using a file-backed shared memory object in /dev/shm.
- Configure port forwarding for easy SSH access.
- Ensure KASLR is disabled (nokaslr) for repeatable experiments.

*Hardened Target (launch_hardened_guest.sh):*
- Launch QEMU guest with a virtual IOMMU (-device intel-iommu).
- Pass kernel arguments to the guest to enable IOMMU usage (intel_iommu=on).

*QMP Socket (/scripts/launch/):*
- Add functionality to all launch scripts to expose a QMP socket for advanced introspection.

### Phase 2: Tool Integration (/src/analysis)

**[ ] PCILeech Wrapper (/src/analysis/pcileech_wrapper.py):**
- Create a Python wrapper to simplify common PCILeech commands.
- Functions for dump, search, write, and mounting the filesystem.
- Automatically construct the -device 'qemu://shm=...' argument.

**[ ] MemProcFS Integration (/scripts/launch/mount_memprocfs.sh):**
- Script to automatically mount a running guest's memory using MemProcFS.
- Handle permissions (sudo) and automatically point to the shared memory file and QMP socket.
- Provide an unmount.sh script for clean shutdown.

**[ ] Memflow Connector (/src/analysis/memflow_connector.rs):**
- Develop a Rust module that uses the memflow-qemu connector.
- Provide simple functions for reading/writing physical memory and listing processes as a proof-of-concept.
- Document the CAP_SYS_PTRACE permission requirement.

### Phase 3: Attack Modules (/src/attacks)

**[ ] Linux Attack Library (/src/attacks/linux_attacks.py):**
- Module to find and patch the pam_unix.so password verification function.
- Module to dump credentials from memory.
- Module to inject a simple kernel-level "hello world" implant.

**[ ] Windows Attack Library (/src/attacks/windows_attacks.py):**
- Module to find and patch the MsvpPasswordValidate function for password bypass.
- Module to dump LSASS process memory.
- Module to extract secrets using known signatures.

**[ ] IOMMU Test Suite (/src/analysis/iommu_tests.py):**
- Develop a test suite that runs all attack modules against the hardened guest.
- Verify that all attacks fail and log the output.
- Generate a simple report on IOMMU effectiveness.

### Phase 4: Advanced Research

**[ ] Custom PCIe Device Emulation:**
- Research modifying the QEMU source to add a custom, malicious virtual PCIe device.
- Document the build process for a forked QEMU with the custom device.
- Create a simple driver in the guest to interact with the malicious device.

**[ ] IOMMU Bypass Research:**
- Implement proof-of-concept for known IOMMU bypass techniques (e.g., sub-page vulnerabilities, deferred invalidation).
- Use the custom PCIe device to test these bypasses against the hardened guest.

### Phase 5: Usability and Reporting

**[ ] Central Control Script (pasiv.py):**
- Create a main CLI tool to manage the entire framework.
- Commands like pasiv launch vulnerable, pasiv attack password-bypass, pasiv report.

**[ ] Documentation (/docs):**
- Write detailed documentation on setting up the environment.
- Document the architecture of the framework.
- Provide tutorials for adding new attack modules.

**[ ] CI/CD Pipeline:**
- Set up a GitHub Actions workflow to run linters and basic tests on the framework's scripts. 