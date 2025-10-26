"""Test the complete flow: scrape → analyze → generate ideas"""
from idea_generator import IdeaGenerator

print("="*60)
print("TESTING COMPLETE FLOW")
print("="*60)

# Create generator with a new hackathon and past hackathons
generator = IdeaGenerator(
    new_hackathon_url="https://cal-hacks-11-0.devpost.com",
    past_hackathon_urls=[
        "https://treehacks-2023.devpost.com"
    ]
)

print("\n🔧 Setting up Claude API...")
if not generator.setup_claude():
    print("❌ Failed to setup Claude API")
    exit(1)

print("\n📋 Scraping new hackathon rules...")
rules_data = generator.scrape_new_hackathon_rules()
print(f"✓ Rules scraped: {len(rules_data)} sections")

print("\n🏆 Scraping past hackathon winners...")
winners_data = generator.scrape_all_past_hackathons()
print(f"✓ Winners scraped: {len(winners_data)} hackathons")

for hackathon in winners_data:
    print(f"  - {hackathon.get('event_name')}: {len(hackathon.get('winning_projects', []))} winners")

print("\n🤖 Generating ideas with Claude AI...")
print("This will:")
print("  1. Analyze success patterns from past winners")
print("  2. Learn technology trends")
print("  3. Understand what judges look for")
print("  4. Generate 10 ideas that follow new hackathon rules")
print()

ideas = generator.generate_ideas_with_claude(rules_data, winners_data)

if ideas:
    print("\n" + "="*60)
    print("✅ SUCCESS! Ideas generated")
    print("="*60)
    print(f"\nIdeas length: {len(ideas)} characters")
    print(f"Output directory: {generator.output_dir}")
    print(f"\nFirst 500 characters of ideas:")
    print("-"*60)
    print(ideas[:500])
    print("-"*60)
else:
    print("\n❌ FAILED: No ideas generated")
