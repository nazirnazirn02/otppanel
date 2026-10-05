FROM python:3.11-slim-bookworm

WORKDIR /app

# System dependencies aur C/C++ compilers install karna (Playwright aur aiohttp ke liye zaroori)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Playwright browsers install karna
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "bot.py"]
