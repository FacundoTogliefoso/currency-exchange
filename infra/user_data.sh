#!/bin/bash

# Basic EC2 setup for Currency Exchange Platform
# Updates system and installs essential tools

# Update system packages
yum update -y

# Install basic tools needed for any application server
yum install -y \
    htop \
    curl \
    wget \
    git \
    unzip

# Install Docker (for containerized applications)
yum install -y docker
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -a -G docker ec2-user

# Install AWS CLI v2 (for secrets management and deployment)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Create application directory
mkdir -p /opt/currency-exchange
chown ec2-user:ec2-user /opt/currency-exchange

# Log completion
echo "$(date): EC2 instance setup completed" >> /var/log/user-data.log
