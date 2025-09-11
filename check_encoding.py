#!/usr/bin/env python3
"""
Script to check for Chinese characters in Python files and ensure proper encoding
"""

import os
import re
import glob
import sys


def find_chinese_characters(text):
    """Find Chinese characters in text"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return chinese_pattern.findall(text)


def check_file_encoding(filename):
    """Check a single file for Chinese characters"""
    chinese_found = []
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            chinese_chars = find_chinese_characters(line)
            if chinese_chars:
                chinese_found.append((i, line.strip(), chinese_chars))
        
        return chinese_found
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []


def main():
    """Main function to check all Python files"""
    print("Checking for Chinese characters in Python files...")
    print("=" * 50)
    
    # Get all Python files
    python_files = glob.glob("*.py")
    
    total_issues = 0
    
    for filename in python_files:
        chinese_found = check_file_encoding(filename)
        if chinese_found:
            print(f"\n🔍 File: {filename}")
            print("-" * 30)
            for line_num, line, chinese_chars in chinese_found:
                print(f"Line {line_num}: {line}")
                print(f"Chinese characters: {chinese_chars}")
                total_issues += 1
    
    print(f"\n" + "=" * 50)
    if total_issues == 0:
        print("✅ All files clean - no Chinese characters found!")
    else:
        print(f"⚠️  Found {total_issues} lines with Chinese characters")
    
    # Also check encoding settings
    print(f"\n📋 System encoding info:")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    
    # Set console encoding for output
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print("✅ Console encoding set to UTF-8")
    except Exception as e:
        print(f"⚠️  Console encoding issue: {e}")


if __name__ == "__main__":
    main()
