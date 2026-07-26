# AWS EC2 Deployment Guide

## Prerequisites
- AWS account with EC2 access
- SSH key pair created in AWS

## Step 1: Launch EC2 Instance
1. Go to **AWS Console > EC2 > Launch Instance**
2. Name: `lca-platform`
3. AMI: **Ubuntu 22.04 LTS**
4. Instance type: **t3.small** (2 vCPU, 2 GB RAM) - ~$15/mo
5. Key pair: Select or create one
6. Network settings:
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from Anywhere (0.0.0.0/0)
7. Storage: **30 GB** gp3
8. Click **Launch Instance**

## Step 2: Connect to Instance
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## Step 3: Setup Docker
```bash
git clone https://github.com/Soumya-Subhra-Datta/LCA-Platform---AI---Driven-Sustainability-Analysis-for-Metal-Production..git
cd LCA-Platform---AI---Driven-Sustainability-Analysis-for-Metal-Production..

chmod +x deploy/setup-ec2.sh deploy/deploy.sh
./deploy/setup-ec2.sh
```
**Log out and log back in** after setup-ec2.sh completes (for docker group).

## Step 4: Deploy
```bash
cd LCA-Platform---AI---Driven-Sustainability-Analysis-for-Metal-Production..
./deploy/deploy.sh
```

## Step 5: Access
- **App**: `http://YOUR_EC2_PUBLIC_IP`
- **API Docs**: `http://YOUR_EC2_PUBLIC_IP/docs`
- **Login**: `admin` / `admin123`

## Useful Commands
```bash
# View logs
docker compose -f deploy/docker-compose.prod.yml logs -f

# Restart
docker compose -f deploy/docker-compose.prod.yml restart

# Stop
docker compose -f deploy/docker-compose.prod.yml down

# Rebuild and restart
docker compose -f deploy/docker-compose.prod.yml up -d --build
```

## Optional: Add Domain + SSL
```bash
sudo apt-get install -y certbot
sudo certbot --nginx -d yourdomain.com
```
