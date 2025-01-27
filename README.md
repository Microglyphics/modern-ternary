# Modernity Worldview Survey
Interactive ternary chart questionnaire for exploring conceptual frameworks and aggregating responses, with modern and postmodern perspectives.

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js
- Cloud SQL Proxy (included in project root as `cloud_sql_proxy_x64.exe`)

### Database Connection
The application uses Cloud SQL Proxy for secure database connections in development:

1. Start Cloud SQL Proxy (from project root):
```bash
./cloud_sql_proxy_x64.exe -instances=modernity-worldview:us-central1:modernity-db=tcp:3307
```

2. Start the FastAPI backend (in a new terminal):
```bash
cd server
python -m uvicorn main:app --reload
```

3. Start the frontend development server (in a new terminal):
```bash
cd frontend
npm run dev
```

### Environment Configuration
Development environment uses `.env` file in the server directory:
```ini
# Development Database Configuration
DB_HOST=127.0.0.1
DB_USER=app_user
DB_PASSWORD=your_password
DB_NAME=modernity_survey
DB_PORT=3307

# Environment
NODE_ENV=development
PORT=8080
```

Production uses app.yaml configuration with Cloud SQL connection.

## Version History
- v2.0.1: Fixed database connectivity, implemented Cloud SQL Proxy for development
- v2.0.0: Initial consolidation of codebase
- v1.x.x: Previous production versions

## Architecture
- Frontend: SvelteKit
- Backend: FastAPI
- Database: Cloud SQL (MySQL)
- Development: Cloud SQL Proxy for secure database access
- Production: Direct Cloud SQL connection via App Engine