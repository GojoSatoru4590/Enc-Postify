FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Asia/Kolkata"
# Token storage path
ENV CONFIG_PATH="/app/data/config.json"

# Install system packages
# Added: build-essential (GCC) for wasmtime/numpy
RUN apt-get update && apt-get install -y \
    ffmpeg libass-dev fonts-liberation fontconfig \
    git wget pv jq python3-dev \
    mediainfo gcc g++ build-essential \
    libsm6 libxext6 \
    libfontconfig1 libxrender1 libgl1-mesa-glx \
    fonts-dejavu-core fonts-roboto \
 && fc-cache -f \
 && rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /app/data

COPY . .

# Install Python dependencies
# --no-cache-dir helps keep the image size small
RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python3", "-m", "VideoEncoder"]
