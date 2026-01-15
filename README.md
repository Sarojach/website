# Saroj Acharya - Professional Portfolio Website

A complete, production-ready portfolio website for Saroj Acharya, an IT student based in Japan. Built with modern web technologies featuring a responsive frontend and powerful Flask backend.

![Portfolio Preview](https://via.placeholder.com/1200x600?text=Portfolio+Website)

## 🌟 Features

- **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices
- **Modern UI/UX** - Clean, professional design with smooth animations
- **Contact Form** - Fully functional contact form with validation
- **Project Showcase** - Dynamic project gallery with filtering
- **Skills Management** - Display technical skills with proficiency levels
- **Experience Timeline** - Show work experience and learning journey
- **API Backend** - RESTful API for dynamic content management
- **Database Integration** - SQLite/MySQL database support
- **Rate Limiting** - Protection against spam and abuse
- **Email Notifications** - Optional email notifications for contact submissions
- **Analytics** - Track visitor statistics

## 📁 Project Structure

```
saroj-portfolio/
│
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── styles.css           # CSS styling
│   ├── script.js            # JavaScript functionality
│   ├── config.js            # API configuration
│   └── images/              # Image assets
│
├── backend/
│   └── app.py               # Flask application
│
├── database/
│   └── schema.sql           # Database schema
│
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (DO NOT COMMIT)
├── .env.example             # Example environment file
├── .gitignore               # Git ignore rules
├── Procfile                 # Heroku deployment
├── runtime.txt              # Python version
├── README.md                # This file
└── setup.sh                 # Setup script
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional)
- Modern web browser

### Quick Setup (5 minutes)

1. **Clone or Download the Repository**
   ```bash
   git clone https://github.com/saroj/saroj-portfolio.git
   cd saroj-portfolio
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your configuration
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Website**
   - Backend API: `http://localhost:5000`
   - Frontend: Open `frontend/index.html` in your browser or use
   ```bash
   cd frontend
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///saroj_portfolio.db
ADMIN_EMAIL=your-email@example.com
```

### Database Setup

The database is automatically created on first run. For manual setup:

```python
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## 📚 API Documentation

### Base URL
- Development: `http://localhost:5000/api`
- Production: `https://your-domain.com/api`

### Endpoints

#### Projects
- `GET /projects` - Get all projects
- `GET /projects/<id>` - Get single project
- `POST /projects` - Add new project
- `PUT /projects/<id>` - Update project
- `DELETE /projects/<id>` - Delete project

#### Contact
- `POST /contact` - Submit contact form
- `GET /contacts` - Get all contacts (admin)

#### Skills
- `GET /skills` - Get all skills
- `GET /skills/<category>` - Get skills by category
- `POST /skills` - Add new skill

#### Experiences
- `GET /experiences` - Get all experiences
- `POST /experiences` - Add new experience

#### Statistics
- `GET /stats` - Get portfolio statistics

## 🧪 Testing

Create `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Test getting projects
response = requests.get(f"{BASE_URL}/projects")
print(f"Projects: {response.json()}")

# Test contact submission
data = {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Great portfolio!"
}
response = requests.post(f"{BASE_URL}/contact", json=data)
print(f"Contact: {response.json()}")
```

Run tests:
```bash
python test_api.py
```

## 📦 Deployment

### Deploy on Heroku

1. **Create Heroku Account**
   - Go to https://www.heroku.com and sign up

2. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   ```

3. **Deploy**
   ```bash
   # Login
   heroku login
   
   # Create app
   heroku create saroj-portfolio
   
   # Set environment variables
   heroku config:set SECRET_KEY=your-secret-key
   
   # Deploy
   git push heroku main
   
   # Open app
   heroku open
   ```

### Deploy on PythonAnywhere

1. Sign up at https://www.pythonanywhere.com
2. Upload files via Web tab
3. Configure Flask app
4. Enable HTTPS
5. Set custom domain

### Deploy on AWS/Digital Ocean

See detailed guides in `DEPLOYMENT.md`

## 🔐 Security

- Change `SECRET_KEY` in production
- Use HTTPS only
- Set `FLASK_ENV=production`
- Enable CORS properly
- Validate all inputs
- Use environment variables for secrets
- Regular security updates

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -i :5000
kill -9 <PID>
```

### Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies again
pip install -r requirements.txt
```

### Database Errors
```bash
# Reset database
rm saroj_portfolio.db
python app.py
```

### CORS Errors
- Make sure Flask-CORS is installed
- Check CORS configuration in app.py
- Update config.js with correct API URL

## 📊 Performance Tips

- Enable caching headers
- Optimize images
- Minify CSS/JavaScript
- Use CDN for static files
- Database indexes for frequent queries
- Rate limiting for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Saroj Acharya**
- Location: Japan
- Email: saroj@example.com
- GitHub: [@saroj](https://github.com/saroj)
- LinkedIn: [Saroj Acharya](https://linkedin.com/in/saroj)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check console logs in browser
4. Contact via portfolio website

## 🎯 Roadmap

- [ ] Add admin dashboard
- [ ] Email notifications
- [ ] Blog section
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Payment integration
- [ ] Comments on projects

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [Heroku Deployment](https://devcenter.heroku.com/)

## 📈 Version History

### v1.0.0 (Current)
- Initial release
- Core features implemented
- API fully functional
- Responsive design

---

**Happy coding! 🚀**

Last Updated: January 2024