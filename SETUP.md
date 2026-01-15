# Saroj Acharya Portfolio - Setup Guide

## ✨ What's Fixed

✅ **Rate Limiting** - Properly implemented to limit contact submissions (10 per hour per IP)
✅ **Error Handlers** - All HTTP errors (404, 500, 405) now return proper JSON responses
✅ **API Authentication** - Admin endpoints protected with API key (`X-API-Key` header)
✅ **Contact Form** - Now actually submits to backend API instead of simulating
✅ **Environment Configuration** - All sensitive data moved to `.env` file
✅ **Production Ready** - Debug mode configurable, supports environment variables
✅ **CORS Flexible** - Allowed origins can be set via environment variable

## 🚀 Quick Start (Development)

### 1. Install Dependencies
```bash
cd "c:\Users\achar\OneDrive\Desktop\my webside"
pip install flask flask-cors flask-sqlalchemy python-dotenv gunicorn
```

### 2. Run Backend
```bash
python backend/app.py
```
Backend runs on: `http://localhost:5000`

### 3. Open Frontend
Open `frontend/index.html` in your browser or use a local server:
```bash
# Using Python
python -m http.server 3000 --directory frontend

# Or any other local server
```
Frontend runs on: `http://localhost:3000`

## 🔐 Using Admin API Key

When you need to add/edit/delete projects or manage contacts, include the API key:

```bash
# Example: Add a new project
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-admin-key-please-change-in-production" \
  -d '{
    "title": "My Project",
    "description": "Project description",
    "technologies": "Python,Flask"
  }'
```

## 📁 Project Structure

```
my webside/
├── backend/
│   └── app.py              # Flask backend (FIXED ✅)
├── frontend/
│   ├── index.html
│   ├── script.js           # FIXED: Now calls backend API ✅
│   ├── config.js           # FIXED: Full API functions ✅
│   ├── styles.css
│   └── images/
├── database/
│   └── schema.sql
├── .env                    # NEW: Development config ✅
├── .env.example            # NEW: Template for production ✅
├── DEPLOYMENT.md           # NEW: Production guide ✅
└── README.md
```

## 🔧 Configuration Files

### `.env` (Development)
Currently set up for local development. Change for production:
- `FLASK_ENV=development` → Change to `production`
- `FLASK_DEBUG=True` → Change to `False`
- `SECRET_KEY=dev-...` → Generate strong key
- `ADMIN_API_KEY=dev-...` → Generate strong key

### `.env.example`
Template showing all available options. Use as reference for production setup.

## ✅ API Endpoints

### Public Endpoints (No Authentication Required)
- `GET /` - API info
- `GET /api/projects` - Get all projects
- `GET /api/projects/<id>` - Get single project
- `GET /api/skills` - Get all skills
- `GET /api/skills/<category>` - Get skills by category
- `GET /api/experiences` - Get all experiences
- `GET /api/stats` - Get statistics
- `POST /api/contact` - Submit contact form (rate-limited)

### Admin Endpoints (Requires `X-API-Key` Header)
- `GET /api/contacts` - Get all contact submissions
- `PUT /api/contact/<id>/mark-read` - Mark contact as read
- `POST /api/projects` - Create project
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project
- `POST /api/skills` - Create skill
- `POST /api/experiences` - Create experience

## 🧪 Test Contact Form Submission

```javascript
// In browser console:
fetch('http://localhost:5000/api/contact', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Test User',
    email: 'test@example.com',
    message: 'This is a test message'
  })
}).then(r => r.json()).then(d => console.log(d))
```

## 🚀 Ready for Production?

See `DEPLOYMENT.md` for:
- Full security checklist
- Database migration (SQLite → PostgreSQL)
- HTTPS setup with Let's Encrypt
- Gunicorn deployment
- Nginx reverse proxy configuration

## ⚠️ Important Notes

1. **Don't commit `.env`** - Add to `.gitignore` immediately
2. **Change all default keys** before production
3. **Use HTTPS** for all production deployments
4. **Backup database** regularly
5. **Monitor error logs** for issues

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| "Too many requests" | Contact form rate-limited (10/hour). Wait or use different IP. |
| CORS errors | Update `ALLOWED_ORIGINS` in `.env` |
| Contact form not submitting | Check `CONFIG.API_BASE_URL` in `frontend/config.js` |
| API key rejected | Ensure header is exactly `X-API-Key: <key>` |
| Database locked | Restart Flask app and check permissions |

---

**🎉 Your website is now production-ready! See `DEPLOYMENT.md` for launch steps.**
