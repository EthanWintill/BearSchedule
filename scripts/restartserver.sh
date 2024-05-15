#!/bin/bash
cp /home/ec2-user/BearSchedule/instance/site.db /home/ec2-user/BearSchedule/instance/site2.db
rm /home/ec2-user/BearSchedule/instance/site.db
mv /home/ec2-user/BearSchedule/instance/site2.db /home/ec2-user/BearSchedule/instance/site.db
sudo systemctl restart nginx
sudo systemctl restart bear