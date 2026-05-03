#!/bin/bash
# AI English Tutor - One-click deployment
# Run this on your Ubuntu server: bash deploy.sh

set -e

PROJECT_DIR="/home/english_teaching_system"
echo "========================================"
echo " AI English Tutor Deployment"
echo "========================================"

# 1. Stop existing service if any
echo "[1/6] Stopping existing service..."
systemctl stop english-teaching 2>/dev/null || true

# 2. Recreate venv with correct paths
echo "[2/6] Setting up Python virtual environment..."
cd "$PROJECT_DIR"
rm -rf venv
/usr/bin/python3 -m venv venv
venv/bin/pip install -q -r requirements.txt
echo "  -> venv created, dependencies installed"

# 3. Fix DB remnants if using PostgreSQL
echo "[3/6] Checking database..."
if grep -q "postgresql" .env 2>/dev/null; then
    sudo -u postgres psql -d english_db -c "DROP TABLE IF EXISTS homework_records, speaking_sessions CASCADE; DROP TYPE IF EXISTS homework_records, speaking_sessions CASCADE;" 2>/dev/null || echo "  -> DB cleanup (may not be needed)"
fi

# 4. Install systemd service
echo "[4/6] Installing systemd service..."
cp "$PROJECT_DIR/systemd.service.example" /etc/systemd/system/english-teaching.service
systemctl daemon-reload

# 5. Start service
echo "[5/6] Starting service..."
systemctl start english-teaching
sleep 3

# 6. Verify
echo "[6/6] Verifying..."
if systemctl is-active --quiet english-teaching; then
    echo "  -> Service is RUNNING"
    echo ""
    curl -s http://127.0.0.1:8001/ | head -3
    echo ""
    echo "========================================"
    echo " Deployment SUCCESS"
    echo " Access: https://edu.xrzmblog.cn"
    echo "========================================"
else
    echo "  -> Service FAILED to start"
    echo "  -> Check: systemctl status english-teaching"
    echo "  -> Check: journalctl -xeu english-teaching -n 30"
    exit 1
fi
