"""Test the API parsing of ideas"""
import requests
import os

# Find the most recent idea_generation folder
folders = [d for d in os.listdir('.') if d.startswith('idea_generation_')]
latest = sorted(folders)[-1]
ideas_file = os.path.join(latest, 'generated_ideas.txt')

print(f"Testing API parsing for: {ideas_file}")
print("="*70)

# Test the API endpoint
try:
    response = requests.get(f"http://localhost:8000/ideas/{ideas_file}")
    if response.ok:
        data = response.json()
        print(f"✅ API returned {len(data['ideas'])} ideas\n")
        
        for idea in data['ideas']:
            print(f"Idea {idea['number']}: {idea['title']}")
            print(f"  Problem: {idea['problem'][:80]}...")
            print(f"  Technologies: {', '.join(idea['technologies'][:3])}")
            print(f"  Why It Wins: {len(idea['whyItWins'])} reasons")
            print(f"  Roadmap: {len(idea['roadmap'])} steps")
            print()
    else:
        print(f"❌ API error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")
