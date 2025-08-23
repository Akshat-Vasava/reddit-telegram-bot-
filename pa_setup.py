import os
import subprocess

print("🐍 Setting up PythonAnywhere environment...")

# Set environment variables
env_vars = {
    'TELEGRAM_BOT_TOKEN': '8325338066:AAGYEPf8H-4aciCB0VpcAllY3lfF-chu34E',
    'TELEGRAM_CHAT_ID': '-1002811964903',
    'REDDIT_CLIENT_ID': 'aQ2TEqAE01VMSqlbsDLwwcQ',
    'REDDIT_CLIENT_SECRET': 'PBtb_TBxMyzUm4tZuhCwgFNg1SPF1g',
    'REDDIT_USER_AGENT': 'my-bot',
    'CHECK_INTERVAL': '300',
    'MAX_POSTS_PER_CHECK': '10'
}

for key, value in env_vars.items():
    os.environ[key] = value
    print(f"✅ Set {key} = {value}")

print("📦 Installing dependencies...")
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

print("🎉 Setup complete! Run: python run_bot.py")
