#!/usr/bin/env python3
"""
Patch semua stub .h files di UPX source untuk mengganti magic bytes
UPX! (85, 80, 88, 33) dengan random magic (91, 156, 62, 122)
"""
import os
import re
import sys

def patch_stub_files(src_dir):
    stub_dir = os.path.join(src_dir, 'src', 'stub')
    
    if not os.path.exists(stub_dir):
        print(f"[!] Stub directory not found: {stub_dir}")
        return False
    
    # Pattern to match: 85, 80, 88, 33 (UPX!)
    # Also match: 85,80,88,33 (without spaces)
    patterns = [
        (r' 85, 80, 88, 33', ' 91,156, 62,122'),  # with spaces
        (r' 85,80,88,33', ' 91,156,62,122'),       # without spaces  
        (r',85, 80, 88, 33', ',91,156, 62,122'),   # preceded by comma
        (r',85,80,88,33', ',91,156,62,122'),       # preceded by comma, no spaces
    ]
    
    # Also patch second magic bytes: 161, 216, 208, 213 -> 166, 241, 130, 77
    patterns.extend([
        (r'161,216,208,213', '166,241,130, 77'),
        (r'161, 216, 208, 213', '166, 241, 130, 77'),
    ])
    
    total_files = 0
    total_patches = 0
    
    for root, dirs, files in os.walk(stub_dir):
        for filename in files:
            if filename.endswith('.h'):
                filepath = os.path.join(root, filename)
                
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original = content
                patches_in_file = 0
                
                for old, new in patterns:
                    count = len(re.findall(old, content))
                    if count > 0:
                        content = re.sub(old, new, content)
                        patches_in_file += count
                
                if patches_in_file > 0:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"[+] Patched {filename}: {patches_in_file} replacements")
                    total_files += 1
                    total_patches += patches_in_file
    
    print(f"\n[*] Done! Patched {total_patches} occurrences in {total_files} files")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <upx-source-dir>")
        print(f"Example: {sys.argv[0]} ./upx-devel")
        sys.exit(1)
    
    patch_stub_files(sys.argv[1])
