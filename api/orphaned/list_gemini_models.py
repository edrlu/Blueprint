"""List available Gemini models"""
import google.generativeai as genai
from config_settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

print("Available Gemini Models:")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print()
