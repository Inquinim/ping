# Ping

## What is this?
A script to ping your servers and subtensor nodes to ensure they are online. If not, messages are sent to your Discord webhook as they are pinged.

## Use at your own risk. No guarantee it works. No guarantee it won't cause any problems with your servers or subtensor.

## Tested on Ubuntu 20.04
Windows and Mac compatibility unknown.

## Where to run the script?
It's recommended to rent a cloud server (Contabo/GCP/AWS/Oracle/Other). You can run it on your computer with Ubuntu 20.04+; if you turn your computer off, or if there is a network or power outage, the script will stop working.

## Specs
The script is very lightweight. A system with 2GB of RAM and 1-2 cores is plenty.

### Step 1
- Create a Discord server for your notifications.

### Step 2
- Create a general notifications channel (receives messages every x mins that servers were pinged)
- Create a channel for user specific notifications (receives messages if a server or subtensor is down)

### Step 3
Create the webhooks in Discord for each channel which will receive notifications.

### Step 4
Download the repository to your computer.
Run the following command in your terminal:
git clone https://github.com/Inquinim/ping.git

Or, you can use GitHub Desktop.

### Step 5
Fill the user specific webhook(s) into ping_user.py under WEBHOOK_EXAMPLE.
Fill the general webhook into core.py under WEBHOOK_GENERAL.

### Step 6
In ping_user.py, add your server name(s), IP(s) and a True/False value depending on whether you want to check if subtensor responds for that server.

### Step 7
Run the ping_user.py script on your server/computer with: python3 ping_user.py

### Firewall
If you have a firewall in place, allow traffic to your server(s) from your IP or from the cloud server you rent to port 9944

## Important notes
If you ping your servers too frequently you may or may not run into Discord rate limiting and messages may not be sent.
This script does not check that your miners are running. It also doesn't check that your subtensor hasn't encountered other issues.
