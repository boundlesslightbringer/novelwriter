# Deployment Instructions

These files help you deploy the NovelWriter application on an Ubuntu EC2 instance.

## Prerequisites

1.  **EC2 Instance**: Ubuntu 22.04 or later.
2.  **Dependencies**: Python 3.12+, Node.js, Nginx.

## Setup Steps

### 1. Backend Setup

1.  Clone the repository to `/home/ubuntu/novelwriter`.
2.  Set up the Python virtual environment:
    ```bash
    cd /home/ubuntu/novelwriter
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  Copy the systemd service file:
    ```bash
    sudo cp deployment/novelwriter.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable novelwriter
    sudo systemctl start novelwriter
    ```

### 2. Frontend Setup

1.  Build the React application (assuming it's in a `frontend` directory):
    ```bash
    cd /home/ubuntu/novelwriter/frontend
    npm install
    npm run build
    ```

### 3. Nginx Setup

1.  Install Nginx:
    ```bash
    sudo apt update
    sudo apt install nginx
    ```
2.  Copy the Nginx configuration:
    ```bash
    sudo cp deployment/nginx.conf /etc/nginx/sites-available/novelwriter
    sudo ln -s /etc/nginx/sites-available/novelwriter /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default  # Remove default site
    ```
3.  Test and restart Nginx:
    ```bash
    sudo nginx -t
    sudo systemctl restart nginx
    ```

## Access

- **Frontend**: `http://<your-ec2-ip>/`
- **API**: `http://<your-ec2-ip>/api/` (proxied to backend)
