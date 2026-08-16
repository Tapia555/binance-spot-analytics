#!/bin/bash

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv git

# Setup project
mkdir -p ~/crypto-bot
cd ~/crypto-bot

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create .env
cat > .env << 'EOF'
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret
SYMBOL=BTCUSDT
TIMEFRAME=1m
LEVERAGE=10
POSITION_SIZE_USDT=100
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id
EOF

# Create systemd service
sudo tee /etc/systemd/system/crypto-bot.service > /dev/null << 'EOF'
[Unit]
Description=Crypto Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/crypto-bot
Environment="PATH=/home/ubuntu/crypto-bot/venv/bin"
ExecStart=/home/ubuntu/crypto-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable crypto-bot
sudo systemctl start crypto-bot

echo "✅ Bot deployed! Check status: sudo systemctl status crypto-bot"
echo "📊 Logs: sudo journalctl -u crypto-bot -f"
