"""Test scraping past hackathons with organized folders"""
from idea_generator import IdeaGenerator

# Test with multiple past hackathons
generator = IdeaGenerator(
    new_hackathon_url="https://cal-hacks-11-0.devpost.com",
    past_hackathon_urls=[
        "https://treehacks-2023.devpost.com",
        "https://hackmit-2023.devpost.com"
    ]
)

print("Testing organized scraping of past hackathons...")
print("="*60)
winners_data = generator.scrape_all_past_hackathons()

print(f"\n{'='*60}")
print(f"RESULTS: {len(winners_data)} hackathons scraped")
print(f"{'='*60}")
for hackathon in winners_data:
    print(f"\n📂 {hackathon.get('data_folder', 'Unknown')}")
    print(f"   Event: {hackathon.get('event_name', 'Unknown')}")
    print(f"   Winners: {len(hackathon.get('winning_projects', []))}")
    print(f"   URL: {hackathon.get('url', '')}")
