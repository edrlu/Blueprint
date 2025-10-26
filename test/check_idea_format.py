"""Check the actual format of generated ideas"""
import os

folders = [d for d in os.listdir('.') if d.startswith('idea_generation_')]
latest = sorted(folders)[-1]
file = os.path.join(latest, 'generated_ideas.txt')

with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

print("="*70)
print("ACTUAL FORMAT OF GENERATED IDEAS")
print("="*70)
print(content)
