# 🌿 Organic Roots — AI + Blockchain Agricultural Provenance System

An AI-enabled, simulated-blockchain-based smart agricultural supply chain provenance system for specialty products (spices, coffee, tea, millets, organic crops).

## Features

- **Farmer Registration**: Farmers can register crops and batches
- **AI Quality Grading**: Automated quality assessment using machine learning
- **Fraud Detection**: AI-powered anomaly detection in supply chain
- **Demand Forecasting**: Predictive analytics for market trends
- **Blockchain Security**: Simulated blockchain for tamper-proof records
- **QR Verification**: Consumer verification via QR codes
- **Multi-Role Dashboards**: Separate interfaces for Farmers, Admins, and Consumers

## Tech Stack

### Backend
- **FastAPI** (Python) - REST API framework
- **SQLite + SQLAlchemy** - Database and ORM
- **JWT + bcrypt** - Authentication and security
- **Scikit-learn** - AI/ML modules
- **Custom Blockchain** - SHA-256 linked blocks

### Frontend
- **React 18 + Vite** - Modern frontend framework
- **Tailwind CSS** - Utility-first styling
- **React Router v6** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Framer Motion** - Animations

## Quick Start

1. **Setup Backend Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   ```

3. **Run Both Services**:
   ```bash
   # From project root
   ./run.sh
   ```

4. **Access the Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Default Admin Account

- **Email**: admin@organicroots.com
- **Password**: admin123

## Project Structure

```
organic_roots/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   ├── blockchain/         # Blockchain implementation
│   ├── ai/                 # AI modules
│   ├── routes/             # API endpoints
│   ├── models/             # Database models
│   ├── utils/              # Utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── context/        # React context
│   │   ├── hooks/          # Custom hooks
│   │   └── utils/          # Frontend utilities
│   ├── package.json
│   └── vite.config.js
├── qr_codes/              # Generated QR codes
└── run.sh                # Startup script
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Farmer
- `GET /farmer/dashboard` - Farmer statistics
- `POST /farmer/products` - Add new product
- `GET /farmer/batches` - List batches
- `POST /farmer/batches` - Create new batch

### Admin
- `GET /admin/dashboard` - Admin statistics
- `GET /admin/users` - All users
- `GET /admin/batches` - All batches
- `GET /admin/flagged` - Fraud-flagged events

### Consumer
- `GET /consumer/verify/{batch_code}` - Product verification

### Blockchain
- `GET /blockchain/chain` - Full blockchain
- `GET /blockchain/verify` - Verify chain integrity

### AI
- `POST /ai/grade-quality` - Quality grading
- `POST /ai/detect-fraud` - Fraud detection
- `POST /ai/forecast` - Demand forecasting

## Development

This project follows a structured build process. Each component is built and tested before moving to the next.

See `ORGANIC_ROOTS_BUILD_LOG.md` for detailed build progress and decisions made during development.

## License

MIT License - see LICENSE file for details.
