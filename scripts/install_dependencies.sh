#!/bin/bash

# Update package list
sudo apt update

# Install ModemManager and other dependencies
sudo apt install -y \
    modemmanager \
    python3-pip \
    python3-venv \
    usbutils \
    network-manager

# Enable ModemManager service
sudo systemctl enable ModemManager
sudo systemctl start ModemManager

# Add current user to dialout group for serial port access
sudo usermod -a -G dialout $USER

echo "Please log out and log back in for group changes to take effect" 