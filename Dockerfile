FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Set environment variables (optional defaults)
ENV CHECK_INTERVAL=300
ENV MAX_POSTS_PER_CHECK=10
ENV REDDIT_USER_AGENT=my-bot

# Run the bot
CMD ["python", "simple_bot.py"]
