# Automated Data Access Management & Security Governance System

A comprehensive, AI-powered solution for automating data access management across GCP Cloud SQL (PostgreSQL) and Looker Studio, built with modern technologies and best practices.

## 🚀 Features

### Core Capabilities
- **AI-Powered Access Analysis**: Real-time risk assessment using Mistral LLM
- **Unified Access Management**: Single interface for Cloud SQL and Looker Studio
- **Visual Workflow Orchestration**: n8n-powered approval workflows
- **Intelligent Policy Enforcement**: Hugging Face embeddings for semantic policy matching
- **Comprehensive Audit Trail**: Full traceability of all access operations
- **Modern Angular UI**: Responsive, accessible interface with Material Design

### Technical Highlights
- **Local-First Architecture**: Complete data sovereignty with Ollama and local services
- **Vector-Based Policy Search**: Semantic policy matching using ChromaDB
- **Real-Time AI Insights**: Live risk assessment and recommendations
- **Scalable Microservices**: Docker-based deployment with service orchestration
- **Enterprise-Grade Security**: Role-based access control and audit logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular UI    │    │   FastAPI App   │    │   n8n Workflows │
│   (Port 4200)   │◄──►│   (Port 8000)   │◄──►│   (Port 5678)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Ollama LLM    │    │   ChromaDB      │
│   (Port 5432)   │    │   (Port 11434)  │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │   Prometheus    │    │     Grafana     │
│   (Port 6379)   │    │   (Port 9090)   │    │   (Port 3000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and settings management
- **LangChain**: AI/LLM orchestration framework
- **Hugging Face**: Sentence transformers for embeddings
- **PostgreSQL**: Primary database with SQLAlchemy ORM
- **Redis**: Caching and session management

### AI/ML
- **Ollama**: Local LLM server with Mistral model
- **ChromaDB**: Vector database for semantic search
- **Sentence Transformers**: Hugging Face embeddings
- **LangChain**: AI workflow orchestration

### Frontend
- **Angular 17**: Modern TypeScript framework
- **Angular Material**: UI component library
- **RxJS**: Reactive programming
- **TypeScript**: Type-safe development

### Infrastructure
- **Docker & Docker Compose**: Container orchestration
- **n8n**: Visual workflow automation
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Nginx**: Reverse proxy and load balancing

### Cloud Integration
- **Google Cloud SDK**: GCP service integration
- **Cloud SQL Admin API**: PostgreSQL user management
- **Looker Studio API**: Dashboard access management
- **IAM API**: Role and permission management

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Google Cloud Project with enabled APIs
- Service account with appropriate permissions

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd lore_interview
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_SERVICE_ACCOUNT_PATH=./credentials/service-account.json
DATABASE_URL=postgresql://postgres:password@postgres:5432/access_management
REDIS_URL=redis://redis:6379
OLLAMA_BASE_URL=http://ollama:11434
```

### 3. GCP Service Account Setup
```bash
# Create credentials directory
mkdir credentials

# Download your service account key from GCP Console
# and save it as credentials/service-account.json
```

### 4. Start the System
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 5. Access the Application
- **Main Application**: http://localhost:4200
- **API Documentation**: http://localhost:8000/docs
- **n8n Workflows**: http://localhost:5678 (admin/admin123)
- **Grafana Monitoring**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090

## 📖 Usage Guide

### 1. Access Request Workflow

#### Submit a Request
1. Navigate to the Access Request form
2. Fill in requester details and resource information
3. AI will analyze the request in real-time
4. Review AI suggestions and risk assessment
5. Submit the request for approval

#### Approval Process
1. Approvers receive notifications via n8n workflows
2. Review request details and AI analysis
3. Approve, reject, or request modifications
4. Automated provisioning upon approval

#### Access Provisioning
- **Cloud SQL**: Automatic user creation and role assignment
- **Looker Studio**: Dashboard sharing and permission management
- **Audit Logging**: All actions logged with full traceability

### 2. Policy Management

#### Create Access Policies
```json
{
  "resource": "sales-dashboard",
  "service_type": "looker_studio",
  "roles": [
    {
      "name": "read_only",
      "permissions": ["view"],
      "conditions": {
        "department": "sales",
        "data_sensitivity": "internal"
      }
    }
  ],
  "approval_workflow": {
    "approval_required": true,
    "approvers": ["data-owner@company.com"]
  },
  "access_duration": "30d",
  "audit": {
    "enabled": true,
    "log_level": "detailed"
  }
}
```

#### AI-Powered Policy Analysis
- Semantic policy matching using embeddings
- Risk assessment based on historical patterns
- Compliance validation against regulations
- Automated policy recommendations

### 3. Monitoring and Analytics

#### Real-Time Metrics
- Request processing times
- Approval rates and delays
- Policy compliance scores
- Security incident detection

#### AI Insights Dashboard
- Risk trend analysis
- Anomaly detection
- Access pattern insights
- Compliance reporting

## 🔧 Development

### Local Development Setup

#### Backend Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run development server
ng serve --host 0.0.0.0 --port 4200
```

#### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Testing
```bash
# Backend tests
pytest

# Frontend tests
ng test

# E2E tests
ng e2e
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management with Redis

### Data Protection
- Encrypted data transmission (HTTPS)
- Secure password generation
- IP-based access restrictions
- Time-based access controls

### Audit & Compliance
- Comprehensive audit logging
- Immutable audit trail
- Compliance reporting (GDPR, SOX, HIPAA)
- Real-time security monitoring

## 📊 Monitoring & Observability

### Metrics Collection
- Request latency and throughput
- Error rates and availability
- Resource utilization
- Custom business metrics

### Alerting
- Automated anomaly detection
- Policy violation alerts
- System health notifications
- Security incident alerts

### Dashboards
- Real-time system status
- Access request analytics
- Security posture overview
- Compliance reporting

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n access-management
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation at `/docs`

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Core access management functionality
- ✅ AI-powered risk assessment
- ✅ Basic workflow automation
- ✅ Audit logging

### Phase 2 (Next)
- 🔄 Advanced workflow customization
- 🔄 Machine learning for anomaly detection
- 🔄 Integration with additional GCP services
- 🔄 Mobile application

### Phase 3 (Future)
- 📋 Multi-cloud support
- 📋 Advanced AI capabilities
- 📋 Zero-trust architecture
- 📋 Blockchain-based audit trail

---

**Built with ❤️ for secure, scalable data access management** # access_management_automation
