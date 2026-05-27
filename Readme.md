# Telegram Random Moment Archive Bot 📸

A Telegram bot that captures random moments of life through photos.

The bot:
- selects a random unused minute
- sends a Telegram message at that exact time
- user uploads a photo
- photo gets archived permanently

Supports:
- multi-user storage
- persistent disk storage
- Docker deployment
- cloud hosting

---

# Features

- Random minute scheduling
- Sleep hour exclusion
- Telegram bot integration
- Dockerized deployment
- Persistent photo storage
- Persistent database storage
- Multi-user support

---

# Folder Structure

```bash
telegrambot/
├── bot.py
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

Persistent storage:

```bash
/data/photos
/data/db
```

---

# Create .env

Create a `.env` file inside the project root:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

PHOTO_DIR=/data/photos

DB_FILE=/data/db/database.json
```

---

# Install Docker

```bash
sudo apt update
sudo apt install docker.io -y
```

Start Docker:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

---

# Create Persistent Storage Directories

```bash
sudo mkdir -p /data/photos
sudo mkdir -p /data/db
```

---

# Build Docker Image

Run from project root:

```bash
sudo docker build -t telegrambot .
```

---

# Run Container

```bash
sudo docker run -d \
  --name telegrambot \
  --restart always \
  --env-file .env \
  -v /data/photos:/data/photos \
  -v /data/db:/data/db \
  telegrambot
```

---

# Verify Running Container

```bash
sudo docker ps
```

---

# View Logs

```bash
sudo docker logs -f telegrambot
```

---

# Stop Container

```bash
sudo docker stop telegrambot
```

---

# Start Container

```bash
sudo docker start telegrambot
```

---

# Restart Container

```bash
sudo docker restart telegrambot
```

---

# Remove Container

```bash
sudo docker rm -f telegrambot
```

---

# Rebuild After Code Changes

```bash
sudo docker build -t telegrambot .

sudo docker rm -f telegrambot

sudo docker run -d \
  --name telegrambot \
  --restart always \
  --env-file .env \
  -v /data/photos:/data/photos \
  -v /data/db:/data/db \
  telegrambot
```

---

# Telegram Usage

Start bot:

```text
/start
```

The bot will:
1. ask for first photo immediately
2. schedule future random minute notifications
3. archive uploaded photos

---

# Persistent Storage

Photos are stored in:

```bash
/data/photos
```

Database is stored in:

```bash
/data/db/database.json
```

Data survives:
- container rebuilds
- docker restarts
- VM reboots

---

# Tech Stack

- Python
- python-telegram-bot
- APScheduler
- Docker
- Google Cloud VM

---

# Future Ideas

- yearly recap video
- heatmap visualization
- Telegram mini app
- web dashboard
- AI-generated memory montage
