#!/bin/bash
cd /root/BearSchedule
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart nginx
sudo systemctl restart bear