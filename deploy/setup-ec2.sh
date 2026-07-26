#!/bin/bash
# ============================================
# LCA Platform - EC2 Instance Setup Script
# Run this ONCE on a fresh Ubuntu EC2 instance
# ============================================
set -e

echo "=== Updating system ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== Installing Docker ==="
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== Adding user to docker group ==="
sudo usermod -aG docker $USER

echo "=== Docker installed ==="
docker --version
docker compose version

echo ""
echo "=== Setup complete! ==="
echo "Now clone your repo and run deploy.sh:"
echo "  git clone https://github.com/Soumya-Subhra-Datta/LCA-Platform---AI---Driven-Sustainability-Analysis-for-Metal-Production..git"
echo "  cd LCA-Platform---AI---Driven-Sustainability-Analysis-for-Metal-Production.."
echo "  chmod +x deploy/deploy.sh"
echo "  ./deploy/deploy.sh"
