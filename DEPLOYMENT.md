# Organic Roots - Deployment Guide

## Overview
Organic Roots is a comprehensive agricultural supply chain management system with AI-powered quality grading, fraud detection, and blockchain verification.

## System Requirements

### Backend Requirements
- Python 3.8+
- SQLite (included with Python)
- 2GB+ RAM
- 1GB+ disk space

### Frontend Requirements
- Node.js 16+
- npm 7+
- 1GB+ RAM
- 500MB+ disk space

### Optional Requirements
- Docker & Docker Compose (for containerized deployment)
- Git (for version control)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Organic Roots"
```

### 2. Make Startup Script Executable (Linux/Mac)
```bash
chmod +x run.sh
```

### 3. Start All Services
```bash
./run.sh start
```

This will automatically:
- Set up Python virtual environment
- Install backend dependencies
- Start FastAPI backend on port 8000
- Install frontend dependencies  
- Start Vite frontend on port 5173
- Run health checks

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Deployment

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize Database**
```bash
python3 -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

4. **Generate Seed Data**
```bash
python3 utils/seed_data.py
```

5. **Start Backend Server**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

3. **Build for Production**
```bash
npm run build
npm run preview
```

## Environment Configuration

### Backend Environment Variables
Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./organic_roots.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Models
AI_MODEL_PATH=./models/
ENABLE_AI_FEATURES=true

# Blockchain
BLOCKCHAIN_DIFFICULTY=4
MINING_REWARD=10.0
```

### Frontend Environment Variables
Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Organic Roots
VITE_APP_VERSION=1.0.0
```

## Production Deployment

### Option 1: Traditional Server

1. **Backend Production Setup**
```bash
# Install production server
pip install gunicorn

# Start with Gunicorn
cd backend
source venv/bin/activate
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

2. **Frontend Production Setup**
```bash
cd frontend
npm run build

# Serve with a production web server (nginx, apache, etc.)
# Example with python simple server:
cd dist
python3 -m http.server 80
```

3. **Nginx Configuration Example**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: Docker Deployment

1. **Create Dockerfile (Backend)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create Dockerfile (Frontend)**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

3. **Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./organic_roots.db
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

4. **Run with Docker Compose**
```bash
docker-compose up -d
```

## Database Management

### Backup Database
```bash
cp backend/organic_roots.db backup/organic_roots_$(date +%Y%m%d_%H%M%S).db
```

### Restore Database
```bash
cp backup/organic_roots_20240101_120000.db backend/organic_roots.db
```

### Reset Database
```bash
rm backend/organic_roots.db
python3 -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
python3 utils/seed_data.py
```

## Testing

### Run Integration Tests
```bash
./run.sh test
```

### Run Individual Tests
```bash
# Backend tests
cd backend
python3 test_database.py
python3 test_auth.py
python3 test_ai_modules.py
python3 test_api_routes.py

# Integration tests
python3 test_integration.py
```

## Monitoring

### Health Checks
- **Backend Health**: http://localhost:8000/health
- **Database Health**: http://localhost:8000/api/health/database
- **AI Models Status**: http://localhost:8000/api/ai/models-status
- **Blockchain Status**: http://localhost:8000/api/blockchain/verify

### Logs
- **Backend Logs**: `backend.log`
- **Frontend Logs**: `frontend.log`
- **Integration Test Results**: `integration_test_results.json`

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use the startup script
./run.sh stop
./run.sh start
```

2. **Python Module Not Found**
```bash
# Ensure virtual environment is activated
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

3. **Frontend Build Fails**
```bash
# Clear npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
```

4. **Database Connection Error**
```bash
# Check if database file exists
ls -la backend/organic_roots.db

# Recreate database
rm backend/organic_roots.db
python3 -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

5. **AI Models Not Loading**
```bash
# Check AI model directory
ls -la backend/ai/

# Ensure scikit-learn is installed
pip install scikit-learn==1.0.2
```

### Performance Optimization

1. **Backend Optimization**
```bash
# Use production server with multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

2. **Database Optimization**
```bash
# Add indexes to frequently queried columns
# (Handled automatically by SQLAlchemy models)
```

3. **Frontend Optimization**
```bash
# Enable production optimizations
cd frontend
npm run build
```

## Security Considerations

1. **Change Default Secrets**
   - Update `SECRET_KEY` in backend environment
   - Use strong passwords for admin accounts

2. **Enable HTTPS in Production**
   - Configure SSL certificates
   - Update CORS settings

3. **Database Security**
   - Regular backups
   - Limit database access
   - Use environment variables for sensitive data

4. **API Security**
   - Rate limiting
   - Input validation
   - Authentication middleware

## Scaling

### Horizontal Scaling
- Load balancer for multiple backend instances
- Shared database (PostgreSQL/MySQL)
- Redis for session storage

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Cache frequently accessed data

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs in `backend.log` and `frontend.log`
3. Run integration tests to identify problems
4. Check API documentation at http://localhost:8000/docs

## Version History

- **v1.0.0**: Initial release with all core features
- AI-powered quality grading
- Fraud detection system
- Blockchain verification
- QR code generation
- Multi-role authentication
- Supply chain tracking
