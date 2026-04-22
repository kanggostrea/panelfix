FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    xvfb \
    chromium-browser \
    chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Copy semua file
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 7860

# Run agent.py sebagai main entry point
CMD ["python", "agent.py"]
