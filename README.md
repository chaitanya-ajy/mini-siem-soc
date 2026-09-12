# Mini SIEM & SOC Monitoring Dashboard

A lightweight Security Information & Event Management (SIEM) system with Security Operations Center (SOC) dashboard capabilities.

## Features
- 🔐 JWT-based authentication (admin/analyst/viewer roles)
- 📊 Real-time log ingestion and storage
- 🚨 Rule-based threat detection engine
- ⚠️ Alert generation and management
- 📋 Incident tracking and response
- 📈 SOC dashboard with charts and summary metrics
- 🌓 Dark theme SOC UI
- 🐳 Fully Dockerized (MySQL, FastAPI backend, React frontend)

## Architecture
- **Frontend**: React + Vite + React Router
- **Backend**: FastAPI + SQLAlchemy (async MySQL)
- **Database**: MySQL 8.0
- **Authentication**: JWT access/refresh tokens with bcrypt
- **Deployment**: Docker Compose orchestration

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Setup
1. Clone the repository
2. Create `.env` files (see `.env.example` templates)
3. Run: `docker compose up -d`
4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Mode
#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Default Admin Credentials
- Username: admin
- Password: admin123
- (Change immediately after first login!)

## API Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/logs` - Ingest log entry
- `GET /api/logs` - List logs with filters
- `GET/POST /api/alerts` - Alert management
- `GET/POST /api/incidents` - Incident management
- `GET /api/dashboard/summary` - SOC dashboard data

## Threat Detection Rules
Configurable rules stored in database for:
- Brute force login attempts
- Port scanning detection
- SQL injection patterns
- Suspicious IP behavior

## Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## License
MIT