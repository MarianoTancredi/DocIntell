# DocIntell - AI Document Intelligence Platform

A production-ready document intelligence platform that combines document processing, semantic search, and conversational AI using RAG (Retrieval-Augmented Generation) architecture.

## 🚀 Features

- **Document Processing**: Upload and process PDF, TXT, DOC, and DOCX files with OCR support
- **Semantic Search**: Vector-based document search using OpenAI embeddings and ChromaDB
- **Conversational AI**: Chat interface for asking questions about your documents
- **User Management**: Secure authentication and user-specific document storage
- **Real-time Monitoring**: Prometheus metrics and Grafana dashboards
- **Scalable Architecture**: Containerized with Docker and Kubernetes support
- **CI/CD Pipeline**: Automated testing, building, and deployment with GitHub Actions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ChromaDB      │    │     Redis       │
                       │   (Vectors)     │    │   (Cache/Queue) │
                       └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (LLM/Embed)   │
                       └─────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM with async support
- **ChromaDB** - Vector database for embeddings
- **OpenAI API** - LLM and embedding models
- **Celery** - Distributed task queue
- **Redis** - Caching and message broker
- **Prometheus** - Metrics collection

### Frontend
- **React 18** - UI framework with hooks
- **Material-UI** - Component library
- **TypeScript** - Type-safe JavaScript
- **Zustand** - State management
- **React Query** - Server state management
- **Vite** - Build tool and dev server

### Infrastructure
- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **GitHub Actions** - CI/CD pipeline
- **Helm** - Kubernetes package manager
- **Grafana** - Monitoring dashboards

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- OpenAI API key

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/docintell.git
cd docintell
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` and add your OpenAI API key:
```bash
OPENAI_API_KEY=your-api-key-here
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Prometheus: http://localhost:9090

### Local Development

#### Backend Setup

```bash
cd backend
pip install poetry
poetry install
poetry shell

# Set up database
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run start
```

## 📖 Usage

### 1. User Registration
Create an account at http://localhost:3000/register

### 2. Document Upload
- Navigate to the Documents page
- Drag and drop or click to upload supported files
- Wait for processing to complete

### 3. Chat with Documents
- Go to the Chat page
- Ask questions about your uploaded documents
- View sources and similarity scores

### 4. Monitor Performance
- Access Prometheus at http://localhost:9090
- View metrics dashboards in Grafana (if configured)

## 🧪 Testing

### Backend Tests
```bash
cd backend
poetry run pytest --cov=app
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### End-to-End Tests
```bash
# Start services
docker-compose up -d

# Run performance tests
docker run --rm --network host \
  -v $(pwd)/scripts:/scripts \
  loadimpact/k6:latest run /scripts/performance-test.js
```

## 🚀 Deployment

### Docker Production

```bash
# Build and deploy production stack
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/k8s/

# Or use Helm
helm install docintell deployment/helm/
```

### Environment Variables

Key production environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM/embeddings | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `DATABASE_URI` | PostgreSQL connection string | Yes |

## 📊 Monitoring

The platform includes comprehensive monitoring:

- **Request Metrics**: Response times, error rates, throughput
- **Business Metrics**: Document processing, chat interactions
- **Infrastructure Metrics**: Database performance, queue status
- **Custom Dashboards**: Grafana visualizations

Access metrics at `/metrics` endpoint for Prometheus scraping.

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation and sanitization
- SQL injection prevention
- Rate limiting (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run the test suite: `npm test` and `poetry run pytest`
5. Submit a pull request

## 📄 API Documentation

Interactive API documentation is available at `/docs` when running the backend server.

Key endpoints:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/documents/upload` - Document upload
- `POST /api/v1/chat/` - Chat with documents
- `GET /api/v1/chat/conversations` - List conversations

## 🐛 Troubleshooting

### Common Issues

**Documents not processing:**
- Check OpenAI API key is valid
- Verify file format is supported
- Check Docker container logs

**Chat not working:**
- Ensure documents are fully processed
- Verify ChromaDB is running
- Check OpenAI API quota

**Performance issues:**
- Monitor resource usage
- Scale containers horizontally
- Check database performance
