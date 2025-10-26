"""
Test Claude API connection
"""
import anthropic
from config_settings import CLAUDE_API_KEY

print("Testing Claude API connection...")
print(f"API Key: {CLAUDE_API_KEY[:20]}...")

try:
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    print("\nSending test message...")
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello, API is working!' and nothing else."
            }
        ]
    )
    
    response = message.content[0].text
    print(f"\n✅ SUCCESS! Claude responded: {response}")
    print("\nAPI is working correctly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Check your internet connection")
    print("2. Verify API key is valid at https://console.anthropic.com/")
    print("3. Check if firewall/VPN is blocking the connection")
    print("4. Try again in a few minutes (might be rate limited)")
