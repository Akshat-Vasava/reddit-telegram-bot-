import os
import time
import logging
import requests
from datetime import datetime, timezone
import praw
import telebot
from telebot.apihelper import ApiException

# Koyeb-specific setup
if 'KOYEB' in os.environ or 'KOYEB_APP' in os.environ:
    print("🚀 Running on Koyeb...")
    # Koyeb handles environment variables automatically
else:
    # Local development - load from .env file
    from dotenv import load_dotenv
    load_dotenv()
    print("💻 Running locally...")

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'my-bot')
REDDIT_TARGET_USER = "ClashDotNinja"
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
MAX_POSTS_PER_CHECK = int(os.getenv('MAX_POSTS_PER_CHECK', 10))
DATA_FILE = 'data/processed_posts.txt'
LOG_FILE = 'logs/bot.log'

# Validate required settings
required_vars = [
    ('TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN),
    ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
    ('REDDIT_CLIENT_ID', REDDIT_CLIENT_ID),
    ('REDDIT_CLIENT_SECRET', REDDIT_CLIENT_SECRET)
]

missing_vars = [var for var, value in required_vars if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize clients
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)
telegram_bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def load_processed_posts():
    """Load processed posts from file"""
    processed_posts = set()
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                for line in f:
                    processed_posts.add(line.strip())
    except Exception as e:
        logger.error(f"Error loading processed posts: {e}")
    return processed_posts

def save_processed_posts(processed_posts):
    """Save processed posts to file"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w') as f:
            for post_id in processed_posts:
                f.write(f"{post_id}\n")
    except Exception as e:
        logger.error(f"Error saving processed posts: {e}")

def download_image(image_url, filename):
    """Download image from URL"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        return False

def is_image_url(url):
    """Check if URL is an image"""
    if not url:
        return False
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def send_image_to_telegram(image_path):
    """Send image to Telegram without caption"""
    try:
        with open(image_path, 'rb') as photo:
            telegram_bot.send_photo(
                TELEGRAM_CHAT_ID,
                photo
            )
        logger.info("Image sent to Telegram successfully")
        return True
    except ApiException as e:
        logger.error(f"Failed to send image to Telegram: {e}")
        return False

def get_image_url(submission):
    """Extract image URL from Reddit submission"""
    # Check for image in preview
    if hasattr(submission, 'preview') and submission.preview:
        return submission.preview['images'][0]['source']['url']
    
    # Check if direct image link
    if not submission.is_self and is_image_url(submission.url):
        return submission.url
    
    # Check for gallery posts
    if hasattr(submission, 'media_metadata') and submission.media_metadata:
        # Get first image from gallery
        for media_id, media in submission.media_metadata.items():
            if media['e'] == 'Image':
                return media['s']['u']
    
    return None

def get_new_posts():
    """Get new posts from the target user"""
    try:
        user = reddit.redditor(REDDIT_TARGET_USER)
        posts = []
        
        for submission in user.submissions.new(limit=MAX_POSTS_PER_CHECK):
            image_url = get_image_url(submission)
            
            # Only process posts with images
            if image_url:
                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'image_url': image_url
                }
                posts.append(post_data)
        
        logger.info(f"Retrieved {len(posts)} image posts from u/{REDDIT_TARGET_USER}")
        return posts
        
    except Exception as e:
        logger.error(f"Error fetching posts from Reddit: {e}")
        return []

def check_and_forward_posts():
    """Check for new posts and forward them to Telegram"""
    logger.info("Checking for new image posts...")
    
    processed_posts = load_processed_posts()
    posts = get_new_posts()
    new_posts = []
    
    for post in posts:
        if post['id'] not in processed_posts:
            new_posts.append(post)
            processed_posts.add(post['id'])
    
    # Process new image posts
    for post in reversed(new_posts):
        # Download and send image
        image_filename = f"temp_{post['id']}.jpg"
        if download_image(post['image_url'], image_filename):
            if send_image_to_telegram(image_filename):
                logger.info(f"Sent image: {post['title']}")
            # Clean up temporary file
            try:
                os.remove(image_filename)
            except:
                pass
        else:
            logger.error(f"Failed to download image: {post['title']}")
        
        time.sleep(1)  # Avoid rate limiting
    
    # Save processed posts
    save_processed_posts(processed_posts)
    
    logger.info(f"Processed {len(new_posts)} new image posts")
    return len(new_posts)

def main():
    """Main function to run the bot"""
    logger.info("Starting Image-Only Reddit to Telegram bot...")
    
    # Debug: Print environment info
    logger.info(f"Target user: u/{REDDIT_TARGET_USER}")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    logger.info(f"Max posts per check: {MAX_POSTS_PER_CHECK}")
    
    try:
        while True:
            posts_processed = check_and_forward_posts()
            if posts_processed > 0:
                logger.info(f"✅ Successfully processed {posts_processed} new posts")
            else:
                logger.info("⏭️  No new posts found")
                
            logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.info("Restarting in 60 seconds...")
        time.sleep(60)
        # Auto-restart on critical failure
        main()
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    main()
