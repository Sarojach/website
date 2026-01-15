# Production Deployment Guide

## ✅ Security Checklist

- [ ] Set a strong `SECRET_KEY` in `.env` (min 32 characters)
- [ ] Set a strong `ADMIN_API_KEY` in `.env`
- [ ] Update `ALLOWED_ORIGINS` to your domain(s) only
- [ ] Enable HTTPS with SSL certificate (use Let's Encrypt)
- [ ] Use environment-specific `.env` file (don't commit to git)
- [ ] Remove `FLASK_DEBUG=True` for production
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Set `FLASK_ENV=production`

## 🚀 Before Launching

### 1. Environment Setup
```bash
# Copy and update the .env file
cp .env.example .env

# Edit .env with production values:
# - Generate strong SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"
# - Generate strong ADMIN_API_KEY: python -c "import secrets; print(secrets.token_hex(16))"
# - Set ALLOWED_ORIGINS to your domain
# - Set DATABASE_URL to production database
```

### 2. Database Setup
For **production**, switch from SQLite to PostgreSQL:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set DATABASE_URL in .env:
# DATABASE_URL=postgresql://username:password@hostname:5432/dbname
```

### 3. Install Production Server
```bash
# Install Gunicorn (recommended for production)
pip install gunicorn

# Or use uWSGI
pip install uwsgi
```

### 4. Deploy with Gunicorn
```bash
# Run with Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

# Or with uWSGI
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### 5. HTTPS Setup (Using Nginx + Let's Encrypt)
```bash
# Install Nginx
# On Ubuntu/Debian:
sudo apt-get install nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure Nginx as reverse proxy
sudo nano /etc/nginx/sites-available/default
```

**Nginx Config Example:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 6. Background Tasks (Optional)
For sending emails automatically:
```bash
pip install celery redis
# Configure in app.py for async email sending
```

### 7. Monitoring & Logging
- Set up log rotation
- Monitor server health
- Use error tracking (e.g., Sentry)
- Set up alerts for failures

## 📋 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `production` or `development` |
| `FLASK_DEBUG` | Enable debug mode | `False` (production), `True` (dev) |
| `FLASK_PORT` | Port to run on | `5000` |
| `SECRET_KEY` | Session encryption key | 32+ char random string |
| `ADMIN_API_KEY` | API authentication key | 16+ char random string |
| `DATABASE_URL` | Database connection string | PostgreSQL/MySQL URI |
| `ALLOWED_ORIGINS` | CORS allowed domains | `https://yourdomain.com,https://www.yourdomain.com` |

## 🔒 API Key Usage

For admin endpoints (add/edit/delete projects, contacts, etc.), include header:
```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-admin-api-key" \
  -d '{"title":"Project","description":"...","technologies":"..."}'
```

## 📞 Contact Form Protection

The contact form is rate-limited to **10 submissions per hour per IP address**. This prevents abuse.

## ⚠️ Important Reminders

1. **Never commit `.env` to Git** - Add to `.gitignore`
2. **Always use HTTPS** in production
3. **Backup your database** regularly
4. **Keep dependencies updated** for security patches
5. **Test in staging** before production deployment
6. **Monitor error logs** for issues
7. **Use strong passwords** for database access

## 🐛 Troubleshooting

### "SECRET_KEY environment variable is not set"
→ Set `SECRET_KEY` in `.env` or environment variables

### CORS errors
→ Update `ALLOWED_ORIGINS` to include your frontend domain

### Database connection errors
→ Verify `DATABASE_URL` connection string

### "Too many requests" error
→ Contact form rate-limited; wait before submitting again

## 🆘 Support

For issues, check:
- `.env` file configuration
- Database connectivity
- Firewall/security groups
- Server logs: `tail -f app.log`
