# Trading Bot Backend

Clean, well-structured FastAPI backend for the Trading Bot Platform.

## Architecture

```
backend/
├── app/
│   ├── api/                    # API routes and endpoints
│   │   ├── v1/                # API version 1
│   │   │   ├── endpoints/     # Route handlers
│   │   │   ├── dependencies/  # FastAPI dependencies
│   │   │   └── router.py      # Main API router
│   ├── core/                   # Core application logic
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection & models
│   │   ├── logging.py         # Logging setup
│   │   └── security.py        # Authentication & security
│   ├── models/                 # Data models
│   │   ├── domain/            # Domain models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── database/          # Database models
│   ├── services/               # Business logic layer
│   │   ├── trading/           # Trading services
│   │   ├── backtest/          # Backtesting services
│   │   └── data/              # Data services
│   ├── repositories/           # Data access layer
│   │   ├── symbols.py         # Symbol repository
│   │   ├── trades.py          # Trade repository
│   │   └── backtests.py       # Backtest repository
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── prisma/                     # Prisma ORM
└── main.py                     # Application entry point
```

## Features

- 🏗️ **Clean Architecture**: Separation of concerns with clear layers
- 🔧 **Type Safety**: Full TypeScript-like type safety with Pydantic
- 📊 **Database**: SQLite with Prisma ORM for type-safe queries
- 🔐 **Security**: JWT authentication and role-based access
- 📝 **Documentation**: Auto-generated API docs with OpenAPI
- 🧪 **Testing**: Comprehensive test suite
- 🚀 **Performance**: Async/await throughout for high performance

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- Node.js 18+ (for frontend)

### Installation

1. **Backend Setup**:

```bash
# Install dependencies
uv sync

# Setup database
uv run prisma generate
uv run prisma db push

# Run migrations
uv run alembic upgrade head
```

2. **Frontend Setup**:

```bash
cd frontend
npm install
npm start
```

3. **Start Development**:

```bash
# Backend (Terminal 1)
uv run python main.py

# Frontend (Terminal 2)
cd frontend && npm start
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Development

### Code Style

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test
uv run pytest tests/test_trading.py
```

### Database

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Reset database
uv run prisma db push --force-reset
```

## Deployment

### Production

```bash
# Build frontend
cd frontend && npm run build

# Start production server
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker

```bash
# Build and run
docker-compose up --build
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=file:./data/trading_bot.db

# API Keys
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# Security
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```
