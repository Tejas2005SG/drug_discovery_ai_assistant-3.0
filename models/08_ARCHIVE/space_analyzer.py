"""
Space Analyzer - Find what's taking up 8-10GB on C: drive
"""

import os
import shutil
from pathlib import Path

def get_size(path):
    """Get size of a file or directory in bytes"""
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        try:
            if item.is_file():
                total += item.stat().st_size
        except:
            pass
    return total

def format_size(size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def main():
    print("="*80)
    print("C: DRIVE SPACE ANALYZER")
    print("="*80)
    
    c_drive = Path("C:/")
    
    # Check common space hogs
    targets = [
        c_drive / "Users" / "Tejas" / "AppData" / "Local" / "pip",
        c_drive / "Users" / "Tejas" / "AppData" / "Local" / "Temp",
        c_drive / "Users" / "Tejas" / "AppData" / "Local" / "pip",
        c_drive / "Users" / "Tejas" / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
        c_drive / "Users" / "Tejas" / ".cache",
        c_drive / "Users" / "Tejas" / "AppData" / "Roaming" / "Python" / "Python313" / "cache",
    ]
    
    print("\n📊 CHECKING COMMON SPACE HOGS:")
    print("-"*80)
    
    total_big = 0
    for path in targets:
        if path.exists():
            size = get_size(path)
            total_big += size
            print(f"  {path}")
            print(f"    Size: {format_size(size)}")
    
    # Check Python installation
    python_path = c_drive / "Users" / "Tejas" / "AppData" / "Local" / "Programs" / "Python"
    if python_path.exists():
        print(f"\n🐍 PYTHON INSTALLATION:")
        print("-"*80)
        for item in python_path.iterdir():
            if item.is_dir():
                size = get_size(item)
                total_big += size
                print(f"  {item.name}: {format_size(size)}")
    
    # Check site-packages
    site_packages = c_drive / "Users" / "Tejas" / "AppData" / "Roaming" / "Python" / "Python313" / "site-packages"
    if site_packages.exists():
        print(f"\n📦 SITE-PACKAGES (Libraries):")
        print("-"*80)
        
        # Find biggest packages
        packages = []
        for item in site_packages.iterdir():
            if item.is_dir():
                size = get_size(item)
                packages.append((item.name, size))
        
        packages.sort(key=lambda x: x[1], reverse=True)
        
        print("  Top 15 largest packages:")
        for name, size in packages[:15]:
            print(f"    {name}: {format_size(size)}")
        
        total_big += sum(p[1] for p in packages)
        
        total_size = sum(p[1] for p in packages)
        print(f"\n  TOTAL site-packages: {format_size(total_size)}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDED CLEANUP:")
    print("="*80)
    print("""
1. Clean Temp files:
   - Press Windows Key + R
   - Type: %temp%
   - Delete all files
   - Size: ~1-3 GB

2. Clean pip cache:
   - Run: pip cache purge
   - Size: ~500 MB - 2 GB

3. Clean Python cache (__pycache__):
   - Run this command in project folder:
     for /r %f in (__pycache__) do del /s /q "%f"
   - Size: ~100-500 MB

4. Delete old logs and outputs:
   - Delete: *.json.backup files
   - Delete: trained_enhanced_system_*.json (keep latest)
   - Delete: enhanced_test_results_*.json (keep latest)
   - Size: ~50-200 MB

5. If you want to UNINSTALL RDKit (saves ~2 GB):
   - pip uninstall rdkit
   - You'll need to reinstall to run the model

6. The model itself needs RDKit (~2 GB) for chemical calculations

TOTAL: 8-10 GB is NORMAL for a Python data science environment!
""")
    
    print("\n✅ RUN THESE COMMANDS TO CLEAN SPACE:")
    print("-"*80)
    print("""
# Clean temp files
del /s /q %temp%\\*

# Clean pip cache
pip cache purge

# Clean pycache in project folder
for /r %f in (__pycache__) do del /s /q "%f"

# Delete old backup files
del *.json.backup

# Delete old result files (keep latest 3)
dir /o-d *.json | more
""")

if __name__ == "__main__":
    main()
