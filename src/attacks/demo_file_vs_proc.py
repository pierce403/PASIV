#!/usr/bin/env python3
"""
PASIV DMA Attack Method Comparison
Demonstrates file-backed memory vs /proc/PID/mem approaches
"""

import os
import time
import mmap

def demo_proc_approach():
    """Demonstrate /proc/PID/mem approach (our previous method)"""
    print("🔍 /proc/PID/mem Approach (Previous Method)")
    print("=" * 50)
    print("✅ Pros:")
    print("   - Works with any running VM")
    print("   - No VM reconfiguration needed")
    print("   - Direct access to process memory")
    print("")
    print("❌ Cons:")
    print("   - Requires finding QEMU PID")
    print("   - Process memory layout can be complex")
    print("   - May hit permission/security restrictions")
    print("   - Indirect access through process memory")
    print("")
    print("📋 Example workflow:")
    print("   1. Find QEMU process: ps aux | grep qemu")
    print("   2. Open /proc/PID/mem")
    print("   3. Search through process memory space")
    print("   4. Modify memory via process interface")
    print("")

def demo_file_approach():
    """Demonstrate file-backed memory approach"""
    print("🎯 File-Backed Memory Approach (New Method)")
    print("=" * 50)
    print("✅ Pros:")
    print("   - Direct access to VM RAM")
    print("   - Clean memory layout (VM's actual memory)")
    print("   - No process overhead")
    print("   - More realistic DMA attack simulation")
    print("   - Better performance")
    print("   - Memory persists across VM restarts")
    print("")
    print("❌ Cons:")
    print("   - Requires VM reconfiguration")
    print("   - Uses more disk space (4GB memory file)")
    print("   - Need to restart VM with new config")
    print("")
    print("📋 Example workflow:")
    print("   1. Launch VM with: -object memory-backend-file")
    print("   2. Open /tmp/pasiv_vm_memory.img directly")
    print("   3. Memory map the entire VM RAM")
    print("   4. Direct read/write to VM memory")
    print("")

def show_file_backed_setup():
    """Show the file-backed memory setup"""
    print("⚙️  File-Backed Memory Setup")
    print("=" * 50)
    print("QEMU Command Example:")
    print("""
sudo qemu-system-x86_64 \\
    -object memory-backend-file,id=pc.ram,size=4G,mem-path=/tmp/pasiv_vm_memory.img,share=on \\
    -machine pc-q35-9.2,memory-backend=pc.ram \\
    [... other VM options ...]
""")
    print("Key Parameters:")
    print("   - memory-backend-file: Use file-backed memory")
    print("   - mem-path: Path to memory file")
    print("   - share=on: Allow external access")
    print("   - size=4G: VM RAM size")
    print("")

def demonstrate_access_patterns():
    """Show different access patterns"""
    print("🔬 Memory Access Pattern Comparison")
    print("=" * 50)
    
    memory_file = "/tmp/pasiv_vm_memory.img"
    
    print("File-Backed Access:")
    if os.path.exists(memory_file):
        size = os.path.getsize(memory_file)
        print(f"   Memory file: {memory_file}")
        print(f"   Size: {size:,} bytes ({size / (1024**3):.1f} GB)")
        print("   Access: Direct file I/O + mmap")
        print("   Performance: ~GB/s read/write speeds")
        
        # Quick access demo
        try:
            with open(memory_file, 'rb') as f:
                start_time = time.time()
                sample = f.read(1024 * 1024)  # Read 1MB
                end_time = time.time()
                print(f"   Speed test: 1MB read in {(end_time - start_time)*1000:.2f}ms")
        except Exception as e:
            print(f"   Status: File not accessible ({e})")
    else:
        print(f"   Status: Memory file not found")
        print(f"   Expected: {memory_file}")
        print("   Run: ./src/vm/file_backed_memory_vm.sh to create")
    
    print("")
    print("/proc/PID/mem Access:")
    print("   Target: /proc/[QEMU_PID]/mem")
    print("   Access: Process memory interface")
    print("   Performance: Variable (depends on process state)")
    print("   Complexity: Higher (process memory layout)")

def main():
    print("🎯 PASIV DMA Attack Method Comparison")
    print("=" * 60)
    print("")
    
    demo_proc_approach()
    print("\n" + "-" * 60 + "\n")
    
    demo_file_approach()
    print("\n" + "-" * 60 + "\n")
    
    show_file_backed_setup()
    print("\n" + "-" * 60 + "\n")
    
    demonstrate_access_patterns()
    
    print("\n" + "=" * 60)
    print("🏆 RECOMMENDATION")
    print("=" * 60)
    print("For realistic DMA attack simulation:")
    print("✅ Use file-backed memory approach")
    print("   - More accurate representation of hardware DMA")
    print("   - Direct memory access without OS interference")
    print("   - Better performance and reliability")
    print("")
    print("🚀 Quick Start:")
    print("   1. ./src/vm/file_backed_memory_vm.sh")
    print("   2. ./src/attacks/file_based_dma_attack.py")
    print("   3. Execute DMA attacks directly on VM memory")
    print("")

if __name__ == "__main__":
    main() 