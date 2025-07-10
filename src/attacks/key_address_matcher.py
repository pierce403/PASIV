#!/usr/bin/env python3
"""
PASIV Key-Address Cryptographic Matcher
Properly derives Ethereum addresses from private keys using secp256k1 cryptography
"""

import json
import sys
from pathlib import Path

def derive_address_from_private_key(private_key_hex):
    """
    Derive Ethereum address from private key using proper cryptography
    """
    try:
        # Try to import required cryptographic libraries
        from Crypto.Hash import keccak
        import ecdsa
        from ecdsa import SigningKey, SECP256k1
        
        # Convert hex private key to bytes
        private_key_bytes = bytes.fromhex(private_key_hex)
        
        # Create signing key from private key
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        
        # Get public key
        verifying_key = signing_key.verifying_key
        public_key = verifying_key.to_string()
        
        # Derive Ethereum address from public key
        # Ethereum uses the last 20 bytes of the Keccak-256 hash of the public key
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(public_key)
        address = "0x" + keccak_hash.hexdigest()[-40:]
        
        return address.lower()
        
    except ImportError:
        # Fallback method using eth_keys if available
        try:
            from eth_keys import keys
            private_key = keys.PrivateKey(bytes.fromhex(private_key_hex))
            address = private_key.public_key.to_checksum_address()
            return address.lower()
        except ImportError:
            return None
    except Exception as e:
        return None

def find_private_key_for_address(target_address, json_file):
    """
    Find the private key that derives to the target address
    """
    target_address = target_address.lower().strip()
    if not target_address.startswith('0x'):
        target_address = '0x' + target_address
    
    print(f"🔍 Searching for private key that derives to: {target_address}")
    
    # Load the extraction data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    private_keys = data['findings']['private_keys']
    wallet_addresses = data['findings']['wallet_addresses']
    
    # First check if the target address exists in our extracted addresses
    if target_address not in [addr.lower() for addr in wallet_addresses]:
        print(f"❌ Address {target_address} not found in extracted wallet addresses!")
        print(f"📋 Total addresses extracted: {len(wallet_addresses)}")
        return None
    
    print(f"✅ Target address found in extracted data!")
    print(f"🔑 Checking {len(private_keys)} private keys...")
    
    matches_found = 0
    
    # Try each private key
    for i, private_key in enumerate(private_keys):
        if i % 1000 == 0:
            print(f"Progress: {i}/{len(private_keys)} keys checked...")
        
        try:
            derived_address = derive_address_from_private_key(private_key)
            if derived_address and derived_address.lower() == target_address.lower():
                matches_found += 1
                print(f"\n🎯 MATCH FOUND!")
                print(f"Private Key: {private_key}")
                print(f"Derives to: {derived_address}")
                print(f"Target:     {target_address}")
                return private_key
                
        except Exception as e:
            continue
    
    print(f"\n❌ No cryptographic match found after checking {len(private_keys)} keys")
    print(f"This could mean:")
    print(f"  • The private key wasn't in memory during the dump")
    print(f"  • The key is encrypted/encoded differently")
    print(f"  • The address is from a different wallet or derivation path")
    
    return None

def search_addresses_by_pattern(pattern, json_file):
    """
    Search for addresses matching a pattern
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    wallet_addresses = data['findings']['wallet_addresses']
    pattern = pattern.lower()
    
    matches = [addr for addr in wallet_addresses if pattern in addr.lower()]
    
    print(f"🔍 Addresses containing '{pattern}':")
    for addr in matches[:20]:  # Show first 20 matches
        print(f"  • {addr}")
    
    if len(matches) > 20:
        print(f"  ... and {len(matches) - 20} more")
    
    return matches

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 key_address_matcher.py <json_file> --address <address>")
        print("  python3 key_address_matcher.py <json_file> --search <pattern>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    if len(sys.argv) >= 4 and sys.argv[2] == "--address":
        target_address = sys.argv[3]
        find_private_key_for_address(target_address, json_file)
    elif len(sys.argv) >= 4 and sys.argv[2] == "--search":
        pattern = sys.argv[3]
        search_addresses_by_pattern(pattern, json_file)
    else:
        print("❌ Invalid arguments. Use --address <address> or --search <pattern>") 