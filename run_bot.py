#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Set environment variables for PythonAnywhere
os.environ['TELEGRAM_BOT_TOKEN'] = '8325338066:AAGYEPf8H-4aciCB0VpcAllY3lfF-chu34E'
os.environ['TELEGRAM_CHAT_ID'] = '-1002811964903'
os.environ['REDDIT_CLIENT_ID'] = 'aQ2TEqAE01VMSqlbsDLwwcQ'
os.environ['REDDIT_CLIENT_SECRET'] = 'PBtb_TBxMyzUm4tZuhCwgFNg1SPF1g'
os.environ['REDDIT_USER_AGENT'] = 'my-bot'
os.environ['CHECK_INTERVAL'] = '300'
os.environ['MAX_POSTS_PER_CHECK'] = '10'

print(f"🚀 Starting Reddit to Telegram Bot on PythonAnywhere...")
print(f"⏰ Started at: {datetime.now()}")

# Import and run your bot
try:
    from simple_bot import main
    main()
except KeyboardInterrupt:
    print("🛑 Bot stopped by user")
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔄 Restarting in 30 seconds...")
    time.sleep(30)
    # Auto-restart on failure
    os.execv(sys.executable, ['python'] + sys.argv)
