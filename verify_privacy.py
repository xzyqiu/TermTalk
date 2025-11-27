#!/usr/bin/env python3
"""
Privacy Verification Script for TermTalk

This script checks that all privacy protections are properly implemented.
Run this after code changes to ensure no privacy regressions.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.privacy import get_privacy_info, verify_no_persistent_identifiers


def check_imports():
    """Check that forbidden modules are not imported."""
    print("[CHECK] Checking for forbidden imports...")
    
    forbidden = {
        'uuid': ['src/room/manager.py'],
        'platform': ['src/crypto/handshake.py', 'src/crypto/box.py', 'src/transport/socket_handler.py'],
    }
    
    violations = []
    
    for module, files in forbidden.items():
        for filepath in files:
            full_path = os.path.join(os.path.dirname(__file__), '..', filepath)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                    # Check for actual import, not just mentions in comments
                    if f"import {module}" in content.replace('#', ''):
                        violations.append(f"{filepath} imports {module}")
    
    if violations:
        print("  [FAIL] Found forbidden imports:")
        for v in violations:
            print(f"     - {v}")
        return False
    else:
        print("  [PASS] No forbidden imports found")
        return True


def check_privacy_status():
    """Verify privacy status flags."""
    print("\n[CHECK] Checking privacy status...")
    
    info = get_privacy_info()
    
    expected = {
        "mac_address_exposed": False,
        "hostname_exposed": False,
        "system_info_exposed": False,
        "uses_ephemeral_ids": True,
        "secure_randomness": True,
        "session_only_identifiers": True,
    }
    
    all_good = True
    for key, expected_value in expected.items():
        actual_value = info.get(key)
        if actual_value == expected_value:
            status = "[PASS]"
        else:
            status = "[FAIL]"
            all_good = False
        
        print(f"  {status} {key}: {actual_value} (expected: {expected_value})")
    
    return all_good


def check_id_generation():
    """Test ID generation for proper format and randomness."""
    print("\n[CHECK] Checking ID generation...")
    
    from src.utils.privacy import generate_anonymous_room_id, generate_anonymous_peer_id
    
    # Test Room IDs
    room_ids = [generate_anonymous_room_id() for _ in range(50)]
    if len(set(room_ids)) == 50:
        print("  [PASS] Room IDs are unique (50/50 samples)")
    else:
        print(f"  [FAIL] Room IDs have collisions ({len(set(room_ids))}/50 unique)")
        return False
    
    if all(len(rid) == 16 for rid in room_ids):
        print("  [PASS] Room IDs are 16 characters")
    else:
        print("  [FAIL] Room IDs have incorrect length")
        return False
    
    if all(all(c in '0123456789abcdef' for c in rid) for rid in room_ids):
        print("  [PASS] Room IDs are valid hex")
    else:
        print("  [FAIL] Room IDs contain non-hex characters")
        return False
    
    # Test Peer IDs
    peer_ids = [generate_anonymous_peer_id() for _ in range(50)]
    unique_count = len(set(peer_ids))
    if unique_count >= 45:  # Allow some collisions in 6-char space
        print(f"  [PASS] Peer IDs are mostly unique ({unique_count}/50 samples)")
    else:
        print(f"  [FAIL] Peer IDs have too many collisions ({unique_count}/50 unique)")
        return False
    
    if all(len(pid) == 6 for pid in peer_ids):
        print("  [PASS] Peer IDs are 6 characters")
    else:
        print("  [FAIL] Peer IDs have incorrect length")
        return False
    
    return True


def check_registry_privacy():
    """Verify registry only stores ephemeral data."""
    print("\n[CHECK] Checking registry privacy...")
    
    import tempfile
    import json
    from src.room.registry import RoomRegistry
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        registry_path = f.name
    
    try:
        registry = RoomRegistry(registry_path)
        registry.register_room("test1234abcd5678", "127.0.0.1", 9999, 9999999999.0)
        
        with open(registry_path, 'r') as f:
            data = json.load(f)
        
        allowed_keys = {'host_ip', 'host_port', 'expires_at'}
        forbidden_keys = {'hostname', 'username', 'mac_address', 'system', 'platform'}
        
        violations = []
        for room_id, room_data in data.items():
            extra_keys = set(room_data.keys()) - allowed_keys
            if extra_keys:
                violations.extend(extra_keys)
            
            forbidden_found = set(room_data.keys()) & forbidden_keys
            if forbidden_found:
                violations.extend(forbidden_found)
        
        if violations:
            print(f"  [FAIL] Registry contains forbidden keys: {violations}")
            return False
        else:
            print("  [PASS] Registry only stores ephemeral data")
            return True
    
    finally:
        if os.path.exists(registry_path):
            os.unlink(registry_path)


def main():
    """Run all privacy checks."""
    print("=" * 60)
    print("TermTalk Privacy Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", check_imports()))
    results.append(("Privacy Status", check_privacy_status()))
    results.append(("ID Generation", check_id_generation()))
    results.append(("Registry Privacy", check_registry_privacy()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for check_name, passed in results:
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {check_name}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] All privacy checks passed!")
        print("TermTalk is properly protecting user privacy.")
        return 0
    else:
        print("\n⚠️  Some privacy checks failed!")
        print("Please review the output above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
