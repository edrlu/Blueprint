"""
Quick test of the idea generator workflow
"""

from idea_generator import IdeaGenerator

def test_basic_workflow():
    """Test the basic workflow with minimal scraping"""
    print("="*60)
    print("TESTING IDEA GENERATOR")
    print("="*60)
    
    # Use a real hackathon URL for testing
    new_hackathon = "https://cal-hacks-11-0.devpost.com"
    
    # Use just 2 past hackathons for quick testing
    past_hackathons = [
        "https://calhacks-10-0.devpost.com",
        "https://treehacks-2024.devpost.com"
    ]
    
    print(f"\nNew Hackathon: {new_hackathon}")
    print(f"Past Hackathons: {len(past_hackathons)}")
    
    # Create generator
    generator = IdeaGenerator(
        new_hackathon_url=new_hackathon,
        past_hackathon_urls=past_hackathons
    )
    
    print("\n✓ Generator created")
    print(f"✓ Output directory: {generator.output_dir}")
    
    # Test Claude setup
    if generator.setup_claude():
        print("✓ Claude API configured")
    else:
        print("✗ Claude API failed")
        return False
    
    print("\n" + "="*60)
    print("Test completed successfully!")
    print("="*60)
    print("\nTo run full workflow:")
    print(f"  python idea_generator.py {new_hackathon}")
    
    return True

if __name__ == "__main__":
    test_basic_workflow()
