# Expense Tracker

A Flask-based expense tracking web application allowing users to add expenses, filter reports by date, and convert currencies.

## Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker

2. Create and activate virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate

3. Install dependencies:

    ```bash
    pip install -r requirements.txt

4. Run the app locally:

    ```bash
    flask run

Access the app at http://127.0.0.1:5000

## Deployment on Web01 and Web02
1. Copy project files to both servers via SSH or Git.

2. On each server:

    ```bash
    sudo apt update
    sudo apt install python3-venv python3-pip -y
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Create a systemd service file at:

    ```bash
    sudo nano /etc/systemd/system/expense_tracker.service

    Paste the following:

    ```bash
    [Unit]
    Description=Gunicorn instance to serve expense_tracker
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/expense_tracker
    ExecStart=/home/ubuntu/expense_tracker/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 main:app

    [Install]
    WantedBy=multi-user.target

4. Start and enable the service:

    ```bash
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl start expense_tracker
    sudo systemctl enable expense_tracker

5. Install and configure Nginx:

    ```bash
    sudo apt install nginx -y

    Then:

    ```bash
    sudo nano /etc/nginx/sites-available/expense_tracker

    Paste:

    ```bash
    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    Enable and reload:

    ```bash
    sudo ln -s /etc/nginx/sites-available/expense_tracker /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl reload nginx

## Load Balancer (HAProxy) Configuration
On the load balancer server:

    ```bash
    sudo apt install haproxy -y

    Edit the HAProxy config:

    ```bash
    sudo nano /etc/haproxy/haproxy.cfg

    Add:

    frontend http_front
        bind *:80
        default_backend http_back

    backend http_back
        balance roundrobin
        server web01 52.70.25.100:80 check
        server web02 34.226.246.26:80 check

    Restart HAProxy:

    ```bash
    sudo systemctl restart haproxy

    Testing Load Balancer:
    
    Visit the Load Balancer’s IP in a browser.

    Refresh the page multiple times.

    Observe logs or add a unique header per server to confirm that requests alternate between Web01 and Web02.