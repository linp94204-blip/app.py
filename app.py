import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Starting the Main Entry Point Application...")

try:
    # Import and run your actual bot code
    import telegram_bot_enhanced
except Exception as e:
    print(f"❌ CRITICAL ERROR during bot startup: {e}")
    sys.exit(1)
