"""Test the breakdown endpoint"""
import requests
import json

# Test data
test_idea = {
    "title": "EcoChain.AI",
    "problem": "Urban waste management systems lack efficient sorting and recycling processes",
    "solution": "AI-powered decentralized waste management system",
    "technologies": ["Python", "TensorFlow", "React", "Fetch.ai"]
}

print("Testing /breakdown endpoint...")
print("="*60)

try:
    response = requests.post(
        "http://localhost:8000/breakdown",
        json={
            "idea": test_idea,
            "hackathon_folder": "idea_generation_20251025_191429"
        },
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✅ Success!")
        print(f"Has Schedule: {data.get('has_schedule')}")
        print(f"\nBreakdown Preview (first 500 chars):")
        print("-"*60)
        print(data.get('breakdown', '')[:500])
        print("-"*60)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
