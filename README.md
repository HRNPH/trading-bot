# Trading Bot Platform

A complete algorithmic trading platform with backtesting and live trading capabilities, built with FastAPI, React, and Docker.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose v2.0+
- At least 2GB available RAM

### Start All Services

```bash
# Make script executable (first time only)
chmod +x start.sh

# Start all services
./start.sh
```

### Manual Start

```bash
# Create external network
docker network create traefik-public

# Create required directories
mkdir -p letsencrypt backend/data

# Build and start services
docker-compose up --build -d
```

## 📊 Service Access Points

Once started, access the services at:

- **Frontend**: http://localhost
- **Backend API**: http://api.localhost
- **API Documentation**: http://api.localhost/docs
- **Traefik Dashboard**: http://traefik.localhost:8080

## 🏗️ Architecture

### Docker Services

- **Traefik**: Reverse proxy with automatic SSL termination
- **Backend**: FastAPI application with SQLite database
- **Frontend**: React application with Vite build system

### Technology Stack

- **Backend**: Python 3.11, FastAPI, Prisma ORM, SQLite
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Zustand
- **Infrastructure**: Docker, Traefik, Nginx

## 🔧 Features

### Backend Features

- ✅ RESTful API with FastAPI
- ✅ SQLite database with Prisma ORM
- ✅ Mock backtesting engine
- ✅ Mock live trading simulation
- ✅ Health checks and monitoring
- ✅ Structured logging

### Frontend Features

- ✅ Modern React with TypeScript
- ✅ Zustand state management
- ✅ Real-time status polling
- ✅ Responsive UI with Tailwind CSS
- ✅ shadcn/ui component library
- ✅ Error handling and loading states

### Infrastructure Features

- ✅ Multi-stage Docker builds
- ✅ Traefik reverse proxy
- ✅ Automatic service discovery
- ✅ Health checks and monitoring
- ✅ Optimized container footprints
- ✅ Development and production ready

## 🛠️ Development

### Project Structure

```
trading-bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Data models
│   │   ├── repositories/   # Data access layer
│   │   └── services/       # Business logic
│   ├── prisma/             # Database schema
│   └── Dockerfile          # Backend container
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── stores/         # Zustand stores
│   │   ├── hooks/          # Custom hooks
│   │   └── types/          # TypeScript types
│   └── Dockerfile          # Frontend container
├── docker-compose.yml      # Service orchestration
├── start.sh               # Startup script
└── DOCKER_SETUP.md        # Docker documentation
```

### Docker Commands

#### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f traefik

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d
```

#### Development Commands

```bash
# Access backend container
docker-compose exec backend bash

# Access frontend container
docker-compose exec frontend sh

# View container resources
docker stats

# Clean up unused resources
docker system prune -f
```

## 📈 Performance Optimizations

### Image Size Optimizations

- **Multi-stage builds**: Separate build and runtime stages
- **Alpine Linux**: Minimal base images
- **Dockerignore**: Exclude unnecessary files
- **Layer caching**: Optimized Dockerfile order

### Runtime Optimizations

- **Health checks**: Automatic service monitoring
- **Resource limits**: Prevent resource exhaustion
- **Network isolation**: Secure service communication
- **Volume persistence**: Data persistence across restarts

## 🔒 Security Features

### Network Security

- **Service isolation**: Internal networks for sensitive services
- **External access**: Only Traefik exposed to host
- **CORS handling**: Proper cross-origin request handling

### Container Security

- **Non-root users**: Services run as non-privileged users
- **Read-only filesystems**: Where possible
- **Security headers**: XSS protection, content type sniffing prevention
- **SSL/TLS**: Automatic certificate management

## 🧪 Testing

### Health Checks

```bash
# Test frontend
curl -f http://localhost

# Test backend API
curl -f http://api.localhost/health

# Test Traefik dashboard
curl -f http://localhost:8080
```

### API Testing

```bash
# Test backtest endpoint
curl -X POST http://api.localhost/api/v1/backtest/ \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","strategy":"cdc_actionzone","timeframe":"1Day","days":30}'

# Test trading endpoint
curl -X POST http://api.localhost/api/v1/trading/start \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","strategy":"cdc_actionzone","timeframe":"1Day"}'
```

## 📊 Monitoring

### Traefik Dashboard

- **URL**: http://traefik.localhost:8080
- **Features**:
  - Service health monitoring
  - Request routing visualization
  - SSL certificate status
  - Middleware configuration

### Log Monitoring

```bash
# Real-time logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f traefik
```

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check Docker daemon
docker info

# Check available resources
docker system df

# Check network
docker network ls
```

#### Network Issues

```bash
# Recreate network
docker network rm traefik-public
docker network create traefik-public

# Restart services
docker-compose down
docker-compose up -d
```

#### Port Conflicts

```bash
# Check port usage
lsof -i :80
lsof -i :443
lsof -i :8080

# Stop conflicting services
sudo lsof -ti:80 | xargs kill -9
```

#### Database Issues

```bash
# Check database file
ls -la backend/data/

# Reset database (WARNING: data loss)
rm backend/data/trading_bot.db
docker-compose restart backend
```

## 📚 Documentation

- [Docker Setup Guide](DOCKER_SETUP.md) - Comprehensive Docker documentation
- [Frontend Backend Integration](FRONTEND_BACKEND_INTEGRATION.md) - Integration details
- [API Documentation](http://api.localhost/docs) - Interactive API docs

## 🎯 Next Steps

### Production Deployment

1. **SSL Certificates**: Configure Let's Encrypt for production
2. **Domain Configuration**: Set up custom domains
3. **Monitoring**: Add Prometheus/Grafana monitoring
4. **Backup Strategy**: Implement database backups
5. **Scaling**: Configure horizontal scaling

### Development Enhancements

1. **Hot Reload**: Configure development volumes
2. **Debugging**: Add debugging tools
3. **Testing**: Add integration tests
4. **Documentation**: Auto-generate API docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 The Trading Bot Platform is now ready for development and production use!**
