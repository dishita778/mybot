FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch FIRST (fixes 900MB GPU wheel issue)
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    torchvision==0.17.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy requirements
COPY requirements.txt .

COPY vectorstore ./vectorstore
COPY client_secret.json ./client_secret.json




# Install everything else
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
