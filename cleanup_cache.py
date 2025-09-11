#!/usr/bin/env python3
"""
Cleanup script to remove Python cache files and prevent encoding issues
"""

import os
import shutil
import glob
import sys


def remove_pycache():
    """Remove __pycache__ directories and .pyc files"""
    removed_count = 0
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"Removed: {cache_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {cache_path}: {e}")
    
    # Remove .pyc files
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        try:
            os.remove(pyc_file)
            print(f"Removed: {pyc_file}")
            removed_count += 1
        except Exception as e:
            print(f"Error removing {pyc_file}: {e}")
    
    return removed_count


def main():
    """Main cleanup function"""
    print("🧹 Cleaning up Python cache files...")
    print("=" * 40)
    
    # Remove cache files
    removed_count = remove_pycache()
    
    if removed_count > 0:
        print(f"✅ Cleanup completed - removed {removed_count} cache files")
    else:
        print("✅ No cache files found - already clean!")
    
    # Set console encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print("✅ Console encoding set to UTF-8")
    except AttributeError:
        print("ℹ️  Console encoding configuration not needed for this Python version")


if __name__ == "__main__":
    main()
