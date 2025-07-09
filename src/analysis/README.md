# Analysis Tools

This directory contains memory analysis tools and wrappers for forensic examination of virtual machine targets.

## Purpose

Provide unified interfaces to leading memory forensics frameworks, enabling comprehensive analysis of DMA attack effects and system state examination.

## Planned Analysis Tools

### Memory Forensics Wrappers
- [ ] **pcileech_wrapper.py** - Python interface for PCILeech operations
  - Memory dumping and searching
  - Filesystem mounting capabilities  
  - Automatic QEMU shared memory integration
  - Batch operation support

- [ ] **memflow_connector.rs** - Rust-based memflow integration
  - Physical memory read/write operations
  - Process enumeration and analysis
  - Performance-optimized memory access
  - Cross-platform connector support

### Analysis Utilities
- [ ] **memory_differ.py** - Compare memory states before/after attacks
- [ ] **process_analyzer.py** - Deep process memory examination
- [ ] **signature_scanner.py** - Scan for known attack signatures
- [ ] **timeline_builder.py** - Reconstruct attack sequence from memory

### IOMMU Testing
- [ ] **iommu_tests.py** - Comprehensive IOMMU effectiveness testing
  - Run attack modules against hardened targets
  - Verify protection mechanisms
  - Generate defense effectiveness reports
  - Log bypass attempts and failures

### Reporting Tools
- [ ] **attack_reporter.py** - Generate detailed attack analysis reports
- [ ] **vulnerability_mapper.py** - Map discovered vulnerabilities
- [ ] **defense_evaluator.py** - Assess protection mechanism effectiveness

## Integration Requirements

### PCILeech Integration
- Requires PCILeech framework installation
- Automatic shared memory device configuration
- Support for multiple memory acquisition methods

### MemProcFS Integration  
- Handles mounting/unmounting procedures
- Provides filesystem-like memory access
- Requires appropriate permissions (sudo)

### Memflow Integration
- Rust toolchain required for compilation
- CAP_SYS_PTRACE capability needed
- QEMU connector configuration

## Usage Examples

```python
# PCILeech wrapper usage
from pcileech_wrapper import PCILeechAnalyzer
analyzer = PCILeechAnalyzer("/dev/shm/guest_memory")
processes = analyzer.list_processes()

# IOMMU testing
from iommu_tests import IOMMUTestSuite
suite = IOMMUTestSuite()
results = suite.run_all_tests("hardened_guest")
``` 