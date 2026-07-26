#!/bin/bash
# ============================================
# LCA Platform - Deploy Script
# Run this after setup-ec2.sh
# ============================================
set -e

PROJ_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJ_DIR"

echo "=== Generating secret key ==="
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)

# Create .env.production if it doesn't exist or update SECRET_KEY
if [ ! -f .env.production ]; then
    cp .env.example .env.production
fi
sed -i "s|APP_SECRET_KEY=.*|APP_SECRET_KEY=${SECRET_KEY}|" .env.production

echo "=== Building and starting services ==="
docker compose -f deploy/docker-compose.prod.yml down 2>/dev/null || true
docker compose -f deploy/docker-compose.prod.yml build --no-cache
docker compose -f deploy/docker-compose.prod.yml up -d

echo "=== Waiting for health check ==="
sleep 10
for i in {1..30}; do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        echo "=== LCA Platform is running! ==="
        echo "    URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_EC2_PUBLIC_IP')"
        echo "    Health: http://localhost/health"
        echo "    API Docs: http://localhost/docs"
        echo ""
        echo "    Default login: admin / admin123"
        exit 0
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

echo "=== WARNING: App may not be healthy. Check logs: ==="
docker compose -f deploy/docker-compose.prod.yml logs --tail=50
