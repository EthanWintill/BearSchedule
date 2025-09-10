#!/bin/bash
cd /var/www/BearSchedule
source .venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl restart nginx
sudo systemctl restart bear