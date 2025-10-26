"""Show the complete generated ideas"""
import os

# Find the most recent idea_generation folder
folders = [d for d in os.listdir('.') if d.startswith('idea_generation_')]
if not folders:
    print("❌ No idea generation folders found")
    exit(1)

latest_folder = sorted(folders)[-1]
ideas_file = os.path.join(latest_folder, "generated_ideas.txt")

if os.path.exists(ideas_file):
    with open(ideas_file, 'r', encoding='utf-8') as f:
        ideas = f.read()
    
    print("="*70)
    print("COMPLETE GENERATED IDEAS FROM CLAUDE AI")
    print("="*70)
    print(ideas)
    print("="*70)
    print(f"\nTotal length: {len(ideas)} characters")
    print(f"Ideas count: {ideas.count('### Idea')}")
    print(f"Source: {ideas_file}")
else:
    print("❌ No ideas file found")
