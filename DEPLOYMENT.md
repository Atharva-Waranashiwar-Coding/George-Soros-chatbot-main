# Deployment Guide

This document covers deploying the George Soros Insights Chatbot to production environments.

## Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Platforms](#cloud-platforms)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-deployment Checklist

### Backend Security

- [ ] Change Django `SECRET_KEY` to a strong random value
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] Set `DEBUG=False` in settings.py
- [ ] Configure `ALLOWED_HOSTS` with your actual domain
- [ ] Set up HTTPS/SSL certificate (Let's Encrypt recommended)
- [ ] Verify `CORS_ALLOWED_ORIGINS` points to your frontend domain
- [ ] Ensure Gemini API key is set via environment variable (not in code)
- [ ] Test that all required environment variables are present

### Frontend Optimization

- [ ] Build the frontend for production
  ```bash
  cd soros-ui-main
  npm run build
  ```
- [ ] Verify all API endpoints point to production backend
- [ ] Test error handling and loading states
- [ ] Check console for warnings and errors

### Database

- [ ] Run migrations on production: `python manage.py migrate`
- [ ] Set up regular backups for `db.sqlite3`
- [ ] Consider using PostgreSQL instead of SQLite for production

---

## Backend Deployment

### Option 1: Traditional Server (Linux/Ubuntu)

#### 1. Server Setup

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y postgresql postgresql-contrib  # Optional: if using PostgreSQL
sudo apt-get install -y nginx
```

#### 2. Application Setup

```bash
# Clone repository
git clone <your-repo-url>
cd soros-insights-chatbot/soros-backend-main

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create environment file
cp ../.env.example .env
# Edit .env with production values
nano .env
```

#### 3. Gunicorn Setup

```bash
# Install Gunicorn
pip install gunicorn

# Test Gunicorn
gunicorn soros_backend.wsgi:application --bind 0.0.0.0:8000

# Create systemd service file
sudo nano /etc/systemd/system/soros-backend.service
```

Add the following:

```ini
[Unit]
Description=George Soros Chatbot Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/ubuntu/soros-insights-chatbot/soros-backend-main
Environment="PATH=/home/ubuntu/soros-insights-chatbot/soros-backend-main/venv/bin"
EnvironmentFile=/home/ubuntu/soros-insights-chatbot/soros-backend-main/.env
ExecStart=/home/ubuntu/soros-insights-chatbot/soros-backend-main/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    soros_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable soros-backend
sudo systemctl start soros-backend
```

#### 4. Nginx Configuration

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/soros-backend
```

Add the following:

```nginx
upstream soros_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /home/ubuntu/soros-insights-chatbot/soros-backend-main/staticfiles/;
    }

    location / {
        proxy_pass http://soros_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/soros-backend /etc/nginx/sites-enabled/

# Test Nginx config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

#### 5. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is usually set up automatically
```

### Option 2: PaaS Deployment

#### Heroku (Deprecated but example for reference)

```bash
# Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Add buildpack
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your_secret_key

# Deploy
git push heroku main
```

---

## Frontend Deployment

### Option 1: AWS S3 + CloudFront

```bash
# Build the frontend
cd soros-ui-main
npm run build

# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create S3 bucket
aws s3 mb s3://your-bucket-name

# Upload files
aws s3 sync dist/ s3://your-bucket-name/ --delete

# Configure CloudFront distribution for the bucket
# (Can be done through AWS Console)
```

### Option 2: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd soros-ui-main
netlify deploy --prod --dir=dist
```

### Option 3: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd soros-ui-main
vercel --prod
```

---

## Docker Deployment

### Backend Dockerfile

Create `soros-backend-main/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "soros_backend.wsgi:application"]
```

### Frontend Dockerfile

Create `soros-ui-main/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./soros-backend-main
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=localhost,backend
    volumes:
      - ./soros-backend-main:/app
      - db_data:/app/db
    networks:
      - soros-network

  frontend:
    build: ./soros-ui-main
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - soros-network

volumes:
  db_data:

networks:
  soros-network:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## Cloud Platforms

### Google Cloud Platform

1. **Cloud Run** (Serverless):
   ```bash
   # Deploy backend
   gcloud run deploy soros-backend \
       --source . \
       --region us-central1 \
       --set-env-vars GEMINI_API_KEY=your_key
   ```

2. **App Engine**:
   - Create `app.yaml`
   - Deploy with `gcloud app deploy`

### AWS

1. **Elastic Beanstalk** (Backend):
   ```bash
   eb init -p python-3.11 soros-backend
   eb create soros-backend
   eb deploy
   ```

2. **Amplify** (Frontend):
   - Connect GitHub repository
   - Auto-deploy on push

### Azure

1. **App Service**:
   - Create Web App for Python
   - Deploy via Git or Docker

---

## Monitoring & Maintenance

### Logging

```python
# In settings.py, configure logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/soros-backend/error.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Health Checks

```python
# Add to urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### Performance Monitoring

- Set up New Relic or Datadog APM
- Monitor database query performance
- Track API response times

### Backup Strategy

```bash
# Daily backup
0 2 * * * cd /home/ubuntu/soros-insights-chatbot && \
    tar czf backups/backup-$(date +\%Y\%m\%d).tar.gz \
    soros-backend-main/db.sqlite3 soros-backend-main/chroma_db/
```

### Updates & Security

```bash
# Regular updates
sudo apt-get update && sudo apt-get upgrade -y

# Update Python packages
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Check for security vulnerabilities
pip-audit
```

---

## Troubleshooting

### "502 Bad Gateway"
- Check Gunicorn status: `systemctl status soros-backend`
- Check error logs: `tail -f /var/log/soros-backend/error.log`
- Verify Nginx configuration: `nginx -t`

### "Connection Refused"
- Ensure backend is running
- Check firewall rules
- Verify port bindings

### High Memory Usage
- Increase Gunicorn worker timeout
- Scale database queries
- Use caching (Redis)

---

## Support & Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Documentation](https://docs.docker.com/)
