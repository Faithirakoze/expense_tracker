Expense Tracker Deployment Guide

This document explains how to deploy the Expense Tracker Flask app on two web servers (Web01 & Web02) and configure HAProxy load balancer (Lb01) to distribute traffic.

1. Prerequisites
Three servers with public IPs:

Web01: 52.70.25.100

Web02: 34.226.246.26

Lb01: Your load balancer server

SSH key-based access to all servers

Python 3.8+ installed on Web01 and Web02

sudo privileges on all servers

2. Deploying on Web01 and Web02
2.1 Transfer Application Files
On your local machine, run:


scp -r -i ~/.ssh/school ~/Documents/expense_tracker/expense_tracker ubuntu@<WEB_IP>:/home/ubuntu/
Replace <WEB_IP> with 52.70.25.100 for Web01 and 34.226.246.26 for Web02.

2.2 Setup Python Environment and Install Dependencies
SSH into each web server:


ssh -i ~/.ssh/school ubuntu@<WEB_IP>
cd ~/expense_tracker
sudo apt update
sudo apt install python3-venv python3-pip -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2.3 Run Gunicorn
Start Gunicorn to serve the app on localhost:


gunicorn --workers 3 --bind 127.0.0.1:8000 main:app
Test with:


curl http://127.0.0.1:8000/
You should see the app's HTML.

Stop Gunicorn with Ctrl+C after testing.

2.4 Configure Nginx
Create /etc/nginx/sites-available/expense_tracker with:


server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
Enable site and reload Nginx:


sudo ln -s /etc/nginx/sites-available/expense_tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
Test Nginx serving app:


curl http://127.0.0.1/
You should see your app HTML.

2.5 Setup systemd Service for Gunicorn
Create /etc/systemd/system/expense_tracker.service:


[Unit]
Description=Gunicorn instance to serve Expense Tracker Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/expense_tracker
Environment="PATH=/home/ubuntu/expense_tracker/venv/bin"
ExecStart=/home/ubuntu/expense_tracker/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 main:app

[Install]
WantedBy=multi-user.target
Enable and start service:


sudo systemctl daemon-reload
sudo systemctl enable expense_tracker
sudo systemctl start expense_tracker
sudo systemctl status expense_tracker
Verify app still works: curl http://127.0.0.1/


3. Configure Load Balancer (Lb01)
3.1 Install HAProxy
On the load balancer server:


sudo apt update
sudo apt install haproxy -y

3.2 Configure HAProxy
Edit /etc/haproxy/haproxy.cfg and add:


frontend http_front
    bind *:80
    default_backend web_servers

backend web_servers
    balance roundrobin
    server web01 52.70.25.100:80 check
    server web02 34.226.246.26:80 check
Save file.

3.3 Restart HAProxy

sudo systemctl restart haproxy
sudo systemctl enable haproxy

4. Testing Load Balancing
On any machine, run:


curl http://<LB_IP>/
Reload the command multiple times.
You should receive your app's HTML served alternately by Web01 and Web02 (you can verify by adding server-specific headers or checking server logs).

5. Managing Secrets
Do not hardcode API keys or secrets in code.

Use a .env file loaded via python-dotenv or set environment variables on servers.

Example: Add Environment="API_KEY=your_key" in the systemd service file under [Service].

Keep .env out of version control (.gitignore).