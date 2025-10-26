"""Show the organized data structure"""
import os
import json
from pathlib import Path

print("\n" + "="*60)
print("📁 ORGANIZED DATA STRUCTURE")
print("="*60 + "\n")

# Find all data folders
data_folders = [d for d in os.listdir('.') if d.endswith('_data_20251025_184922')]

for folder in data_folders:
    print(f"📂 {folder}/")
    
    # List files in folder
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        size = os.path.getsize(file_path)
        print(f"   ├─ {file} ({size:,} bytes)")
        
        # Show summary.txt content
        if file == 'summary.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\n   Content:")
                for line in content.split('\n')[:10]:  # First 10 lines
                    print(f"   │  {line}")
                print()

# Show idea generation folders
idea_folders = [d for d in os.listdir('.') if d.startswith('idea_generation_20251025_184922')]

for folder in idea_folders:
    print(f"\n📂 {folder}/")
    
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        size = os.path.getsize(file_path)
        print(f"   ├─ {file} ({size:,} bytes)")
        
        # Show data_index.txt content
        if file == 'data_index.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\n   Content:")
                for line in content.split('\n'):
                    print(f"   │  {line}")
                print()

print("\n" + "="*60)
print("✅ Data is now organized in individual folders!")
print("="*60)
