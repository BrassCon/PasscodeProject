<<<<<<< HEAD
<<<<<<< HEAD
# PasscodeProject
Project with website based on python and DevOps tools.
=======
=======
=======
# PasscodeProject
Project with website based on python and DevOps tools.
=======
>>>>>>> ae49d8d (Add CI pipeline)
>>>>>>> 77443fc (Add CI pipeline)
# Passcode Portal Web App

A minimal Python Flask web application that retrieves messages from PostgreSQL based on passcode input.

## Features

- 🔐 Passcode-based message retrieval
- 🐘 PostgreSQL database integration  
- 🐳 Docker containerization with multi-stage builds
- 📊 Health checks and Prometheus metrics
- 🧪 Comprehensive test suite
- 🔄 Automatic database initialization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker Compose

1. **Clone and start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web app: http://localhost:5000
   - Health check: http://localhost:5000/health  
   - Metrics: http://localhost:5000/metrics

3. **Test with sample passcodes:**
   - `secret123` → "Hello, world!"
   - `admin` → "Welcome, admin!"
   - `test` → "Test message successful!"

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL** (or use Docker):
   ```bash
   docker run --name postgres -e POSTGRES_DB=webapp -e POSTGRES_USER=webapp -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15-alpine
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest test_app.py -v

# Run with coverage
pytest test_app.py --cov=app --cov-report=html

# Run integration tests (requires database)
pytest test_app.py -m integration
```

## Architecture

### Application Structure
```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Multi-stage Docker build
├── docker-compose.yml # Container orchestration
├── init.sql          # Database initialization
├── test_app.py       # Test suite
└── README.md         # This file
```

### Database Schema
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    passcode VARCHAR(50) UNIQUE NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET/POST | Main passcode form |
| `/health` | GET | Health check endpoint |
| `/metrics` | GET | Prometheus metrics |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `db` | PostgreSQL hostname |
| `POSTGRES_DB` | `webapp` | Database name |
| `POSTGRES_USER` | `webapp` | Database username |
| `POSTGRES_PASSWORD` | `password` | Database password |
| `POSTGRES_PORT` | `5432` | Database port |
| `PORT` | `5000` | Application port |
| `FLASK_ENV` | `production` | Flask environment |

### Docker Compose Services

- **app**: Flask application container
- **db**: PostgreSQL 15 database container
- **Volumes**: Persistent data storage for PostgreSQL
- **Networks**: Isolated network for service communication

## Monitoring

### Health Checks
- **Application**: `curl http://localhost:5000/health`
- **Database**: Built-in PostgreSQL health checks
- **Docker**: Automatic container health monitoring

### Prometheus Metrics
- `app_requests_total`: Total number of requests by method and endpoint
- `app_request_duration_seconds`: Request latency histogram

Example metrics output:
```
# HELP app_requests_total Total app requests
# TYPE app_requests_total counter
app_requests_total{endpoint="/",method="GET"} 5.0
app_requests_total{endpoint="/",method="POST"} 3.0
```

## Security Considerations

- Non-root user in Docker container
- Input validation for passcodes
- SQL injection protection via parameterized queries
- No sensitive data in environment variables (use secrets in production)

## Alternative Solutions

### 1. FastAPI Alternative
```python
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
import asyncpg

app = FastAPI()

@app.post("/")
async def submit_passcode(passcode: str = Form(...)):
    # Similar logic with async database operations
    pass
```

### 2. Django Alternative
- Full-featured framework with ORM
- Built-in admin interface
- More complex but feature-rich

### 3. Node.js + Express Alternative
```javascript
const express = require('express');
const { Pool } = require('pg');

const app = express();
const pool = new Pool(/* config */);

app.post('/', async (req, res) => {
    // Similar logic in JavaScript
});
```

### 4. Serverless Alternative
- AWS Lambda + RDS
- Google Cloud Functions + Cloud SQL
- Vercel + PlanetScale

## Production Considerations

1. **Security**:
   - Use proper secrets management
   - Enable HTTPS/TLS
   - Implement rate limiting
   - Add authentication/authorization

2. **Database**:
   - Connection pooling
   - Read replicas for scaling
   - Backup and recovery strategy
   - Database migrations

3. **Monitoring**:
   - Application logging
   - Error tracking (Sentry)
   - Performance monitoring (APM)
   - Alerting systems

4. **Deployment**:
   - CI/CD pipelines
   - Blue-green deployments
   - Container orchestration (Kubernetes)
   - Load balancing

## Troubleshooting

### Common Issues

1. **Database connection failed**:
   ```bash
   # Check if PostgreSQL is running
   docker-compose logs db
   
   # Restart services
   docker-compose down && docker-compose up
   ```

2. **Port already in use**:
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "5001:5000"  # Use different host port
   ```

3. **Permission denied**:
   ```bash
   # Fix file permissions
   chmod +x app.py
   chown -R $(whoami):$(whoami) .
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - feel free to use this code for your projects!
<<<<<<< HEAD
>>>>>>> a572fec (Initial commit)
=======
<<<<<<< HEAD
=======
>>>>>>> ae49d8d (Add CI pipeline)
>>>>>>> 77443fc (Add CI pipeline)
