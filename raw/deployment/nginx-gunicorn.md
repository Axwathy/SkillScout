---
type: deployment
title: "Nginx + Gunicorn Configuration"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, deployment]
---

# Nginx + Gunicorn Configuration

This document covers the production serving stack for the Django backend: **Gunicorn** as the WSGI application server and **Nginx** as the reverse proxy. This configuration is used when deploying to a VPS or bare-metal server rather than a PaaS like Railway.

See also: [[backend-architecture|Backend Architecture]], [[deployment-architecture|Deployment Architecture]]

---

## Architecture

```
Client → Nginx (port 80/443) → Gunicorn (port 8000) → Django
                 ↓
         Static files (direct serve)
         Media files (direct serve)
         SSL termination
         WebSocket proxy (Daphne/Uvicorn)
```

---

## Gunicorn Configuration

### `gunicorn.conf.py`

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"

# Worker processes
#   Recommended formula: 2 * CPU cores + 1
#   For a 2-core machine: 2 * 2 + 1 = 5
workers = 2 * multiprocessing.cpu_count() + 1

# Worker class
#   Use 'gthread' for mixed I/O workloads (API + DB queries)
#   Use 'uvicorn.workers.UvicornWorker' if using ASGI (WebSockets)
worker_class = "gthread"
threads = 4

# Timeouts
timeout = 120          # Kill workers that hang for > 120s
graceful_timeout = 30  # Time for graceful shutdown
keepalive = 5          # Keep-alive connections (seconds)

# Request limits
max_requests = 1000          # Restart worker after N requests (prevents memory leaks)
max_requests_jitter = 50     # Random jitter to avoid all workers restarting at once

# Logging
accesslog = "-"          # stdout
errorlog = "-"           # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "recruitment_saas"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for faster worker spawning
preload_app = True
```

### Worker Sizing Guide

| Machine        | CPU Cores | Workers | Threads | Total Concurrent |
|----------------|-----------|---------|---------|------------------|
| Small (1 vCPU) | 1         | 3       | 4       | 12               |
| Medium (2 vCPU)| 2         | 5       | 4       | 20               |
| Large (4 vCPU) | 4         | 9       | 4       | 36               |
| XL (8 vCPU)    | 8         | 17      | 4       | 68               |

> **Note:** For I/O-bound workloads (typical for web APIs), the thread-based approach with `gthread` worker class provides good throughput without the complexity of async.

---

## Nginx Configuration

### `/etc/nginx/sites-available/recruitment-saas`

```nginx
# Upstream — Gunicorn backend
upstream django_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# Redirect HTTP → HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL Configuration (managed by Certbot / Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Request buffering
    client_max_body_size 25M;         # Max upload size (resumes, etc.)
    client_body_buffer_size 128k;
    proxy_buffering on;
    proxy_buffer_size 4k;
    proxy_buffers 8 16k;
    proxy_busy_buffers_size 32k;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;

    # Static files (collected via collectstatic)
    location /static/ {
        alias /var/www/recruitment-saas/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files (user uploads — resumes, profile images)
    location /media/ {
        alias /var/www/recruitment-saas/media/;
        expires 7d;
        add_header Cache-Control "public";

        # Security: prevent execution of uploaded files
        location ~* \.(php|py|sh|pl|cgi)$ {
            deny all;
        }
    }

    # WebSocket connections (for real-time features)
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;  # Daphne/Uvicorn ASGI server
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;  # 24 hours for long-lived connections
    }

    # Django application (all other requests)
    location / {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check endpoint (no logging)
    location /api/v1/health/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        access_log off;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

---

## SSL Termination

SSL is terminated at Nginx using **Let's Encrypt** certificates managed by Certbot:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.example.com

# Auto-renewal (cron added automatically)
sudo certbot renew --dry-run
```

### SSL Best Practices

- **TLS 1.2+** only — TLS 1.0 and 1.1 are deprecated
- **HSTS** enabled with a 2-year max-age and `preload` flag
- **OCSP stapling** enabled for faster certificate validation
- **Forward secrecy** via ECDHE cipher suites

---

## WebSocket Proxying

For real-time features (e.g., live pipeline updates, notification streams), WebSocket connections are proxied from Nginx to a separate ASGI server:

| Component       | Port  | Purpose                        |
|-----------------|-------|--------------------------------|
| Gunicorn (WSGI) | 8000  | HTTP API requests              |
| Daphne (ASGI)   | 8001  | WebSocket connections          |
| Nginx            | 443   | SSL termination + routing      |

```bash
# Start Daphne alongside Gunicorn
daphne -b 127.0.0.1 -p 8001 config.asgi:application
```

---

## Systemd Service Files

### `gunicorn.service`

```ini
[Unit]
Description=Gunicorn daemon for Recruitment SaaS
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/recruitment-saas
ExecStart=/var/www/recruitment-saas/venv/bin/gunicorn config.wsgi:application -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Common Operations

```bash
# Start / stop / restart
sudo systemctl start gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

# Reload workers gracefully (no downtime)
sudo systemctl reload gunicorn

# View logs
sudo journalctl -u gunicorn -f
```

---

## Performance Tuning

| Parameter               | Default   | Recommended | Reason                                |
|-------------------------|-----------|-------------|---------------------------------------|
| `worker_connections`    | 1024      | 2048        | Handle more concurrent connections    |
| `keepalive_timeout`     | 75s       | 5s          | Free connections faster               |
| `client_max_body_size`  | 1M        | 25M         | Allow resume uploads                  |
| `gzip_comp_level`       | 1         | 6           | Good compression/CPU trade-off        |
| `proxy_buffering`       | on        | on          | Buffer responses from Gunicorn        |

---

## Monitoring

- **Nginx access logs**: `/var/log/nginx/access.log` — analyze with GoAccess or ELK
- **Nginx error logs**: `/var/log/nginx/error.log`
- **Gunicorn stats**: Use `--statsd-host` for StatsD/Prometheus metrics
- **Process monitoring**: Supervisor or systemd for process management
