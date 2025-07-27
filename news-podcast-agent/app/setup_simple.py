#!/usr/bin/env python3
"""
Setup script for the simplified news podcast agent.
"""

import os
import subprocess
import sys

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "python-dotenv==1.0.0",
        "requests==2.31.0", 
        "newsapi-python==0.2.6",
        "google-generativeai==0.3.2",
        "elevenlabs==0.2.26"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def create_env_file():
    """Create .env file with API keys."""
    print("\n🔑 Setting up API keys...")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file already exists")
        return True
    
    print("Please provide your API keys:")
    print("\n📝 Note: You can leave ElevenLabs API key as placeholder if you want to test without audio generation")
    
    google_key = input("Google API Key (for Gemini): ").strip()
    news_key = input("News API Key: ").strip()
    elevenlabs_key = input("ElevenLabs API Key (or press Enter for placeholder): ").strip()
    
    if not google_key or not news_key:
        print("❌ Google API Key and News API Key are required")
        return False
    
    # Use placeholder if no ElevenLabs key provided
    if not elevenlabs_key:
        elevenlabs_key = "your-elevenlabs-api-key-here"
        print("ℹ️  Using placeholder for ElevenLabs API key")
        print("   You can add it later to enable audio generation")
    
    # Create .env file
    env_content = f"""# News Podcast Agent API Keys
GOOGLE_API_KEY={google_key}
NEWS_API_KEY={news_key}
ELEVENLABS_API_KEY={elevenlabs_key}
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ .env file created")
    return True

def test_configuration():
    """Test the configuration."""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import config
        
        # Check required keys
        if not config.google_api_key or config.google_api_key == "your-google-api-key-here":
            print("❌ Google API key is required")
            return False
        
        if not config.news_api_key:
            print("❌ News API key is required")
            return False
        
        # Check ElevenLabs key (optional for testing)
        elevenlabs_key = config.get_elevenlabs_key()
        if elevenlabs_key:
            print("✅ ElevenLabs API key configured - audio generation enabled")
        else:
            print("⚠️  ElevenLabs API key not set - audio generation will be disabled")
            print("   You can still test the agent, but it will create text files instead of audio")
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main setup function."""
    print("🎙️ News Podcast Agent Setup")
    print("=" * 40)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return
    
    # Step 3: Test configuration
    if not test_configuration():
        print("❌ Configuration test failed")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the news podcast agent:")
    print("  python news_podcast_agent.py")
    print("\nTo get API keys:")
    print("  Google API: https://makersuite.google.com/app/apikey")
    print("  News API: https://newsapi.org/")
    print("  ElevenLabs: https://elevenlabs.io/ (free tier available)")
    print("\nNote: The agent will work without ElevenLabs API key,")
    print("      but will create text files instead of audio.")

if __name__ == "__main__":
    main() 