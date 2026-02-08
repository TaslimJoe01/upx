#!/usr/bin/env python3
import os
import re
import sys

def patch_stub_files(src_dir):
    stub_dir = os.path.join(src_dir, 'src', 'stub')
    
    if not os.path.exists(stub_dir):
        print(f"[!] Stub directory not found: {stub_dir}")
        return False
    
    # Patterns to replace in bytecode (decimal byte arrays)
    # Magic bytes: 85, 80, 88, 33 (UPX!) -> random bytes
    # String "UPX-" in ASCII: 85, 80, 88, 45
    # String "upx" in ASCII: 117, 112, 120
    patterns = [
        # UPX! magic
        (r'( 85, 80, 88, 33)', ' 91,156, 62,122'),
        (r'(,85, 80, 88, 33)', ',91,156, 62,122'),
        # UPX! magic2 
        (r'(161,216,208,213)', '166,241,130, 77'),
        (r'(161, 216, 208, 213)', '166, 241, 130, 77'),
        # UPX- string (85,80,88,45) -> null bytes
        (r'( 85, 80, 88, 45)', '  0,  0,  0,  0'),
        (r'(,85, 80, 88, 45)', ', 0,  0,  0,  0'),
        # upx string (117,112,120) -> null bytes
        (r'(117, 112, 120)', '  0,   0,   0'),
        (r'(117,112,120)', '  0,  0,  0'),
    ]
    
    # String patterns in source/asm files
    string_patterns = [
        (r'"UPX-[\d.]+ want', '"error: need'),
        (r'"upx"', '""'),
        (r'"UPX"', '""'),
    ]
    
    total_files = 0
    total_patches = 0
    
    for root, dirs, files in os.walk(stub_dir):
        for filename in files:
            if not (filename.endswith('.h') or filename.endswith('.c') or filename.endswith('.S')):
                continue
                
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            original = content
            patches_in_file = 0
            
            # Apply byte patterns (for .h files)
            if filename.endswith('.h'):
                for pattern, replacement in patterns:
                    count = len(re.findall(pattern, content))
                    if count > 0:
                        content = re.sub(pattern, replacement, content)
                        patches_in_file += count
            
            # Apply string patterns (for .c and .S files)
            for pattern, replacement in string_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    patches_in_file += len(matches)
            
            if patches_in_file > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[+] {filename}: {patches_in_file} patches")
                total_files += 1
                total_patches += patches_in_file
    
    print(f"\n[*] Done! Patched {total_patches} occurrences in {total_files} files")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <upx-source-dir>")
        print(f"Example: {sys.argv[0]} ./upx-devel/upx")
        sys.exit(1)
    
    patch_stub_files(sys.argv[1])
