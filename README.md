# Contractor Intelligence

> An agentic lead intelligence system that autonomously discovers IT service contractor partners, scores them with a self-improving ML model, and generates personalized outreach via LLM agents — with a full data pipeline tracking conversion outcomes.

![Dashboard](https://img.shields.io/badge/Dashboard-Next.js-black?style=flat-square&logo=next.js)
![API](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)
![ML](https://img.shields.io/badge/ML-XGBoost%20%2B%20SHAP-orange?style=flat-square)
![Agents](https://img.shields.io/badge/Agents-CrewAI%20%2B%20Groq-purple?style=flat-square)
![Pipeline](https://img.shields.io/badge/Pipeline-Temporal-blue?style=flat-square)
![Live](https://img.shields.io/badge/Live-Vercel-black?style=flat-square&logo=vercel)

**🔗 Live Demo: [contractor-intel-five.vercel.app](https://contractor-intel-five.vercel.app)**

---

## Screenshots

### Dashboard Overview
![Dashboard](https://raw.githubusercontent.com/Sakshi3027/contractor-intelligence/main/assets/dashboard.png)

### Lead Scoring Table
![Leads Table](https://raw.githubusercontent.com/Sakshi3027/contractor-intelligence/main/assets/leads-table.png)

### Lead Distribution by City
![Chart](https://raw.githubusercontent.com/Sakshi3027/contractor-intelligence/main/assets/chart.png)

---

## What Makes This Different

Most lead generation tools are static scripts. This system:

- **Learns over time** — XGBoost model retrains automatically as outcome data accumulates
- **Multi-agent research** — CrewAI agents research each business before writing personalized outreach
- **Full data flywheel** — Discovery → Scoring → Outreach → Outcomes → Retraining, all automated
- **5 database paradigms** — PostgreSQL, MongoDB, ClickHouse, Qdrant, Redis in one system
- **Production-grade infra** — Temporal workflows, Prometheus monitoring, 11 Docker containers

---

## Tech Stack

### AI / ML
| Tool | Purpose |
|------|---------|
| XGBoost + SHAP | Lead scoring with explainability |
| MLflow | Experiment tracking + model versioning |
| CrewAI | Multi-agent orchestration |
| Groq (llama-3.3-70b) | Ultra-fast LLM inference |

### Data Engineering
| Tool | Purpose |
|------|---------|
| Temporal | Workflow orchestration |
| Apache Flink | Real-time scoring stream |
| dbt | Data transformation layer |

### Databases
| Database | Type | Purpose |
|----------|------|---------|
| PostgreSQL | Relational | Scores, outreach, outcomes |
| MongoDB | Document | Raw profiles, agent research |
| ClickHouse | Columnar | Analytics + funnel metrics |
| Qdrant | Vector | Semantic lead matching |
| Redis | Cache | Job queues + caching |

### Backend + Frontend
| Tool | Purpose |
|------|---------|
| FastAPI | REST API (12 endpoints) |
| Strawberry | GraphQL layer |
| Next.js | Dashboard UI |
| Recharts | Data visualization |

### DevOps
| Tool | Purpose |
|------|---------|
| Docker Compose | 11 containers |
| Prometheus + Grafana | Monitoring |
| GitHub Actions | CI/CD |
| Terraform | GCP IaC |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 18+
- API keys: Google Places, Groq, Hunter.io

### 1. Clone and setup
    git clone https://github.com/Sakshi3027/contractor-intelligence.git
    cd contractor-intelligence
    cp .env.example .env
    # Fill in your API keys in .env

### 2. Start all services
    docker-compose up -d

### 3. Initialize databases
    docker exec -i contractor_postgres psql -U contractor_user -d contractor_db < infrastructure/docker/init_postgres.sql
    docker exec -i contractor_mongodb mongosh < infrastructure/docker/init_mongodb.js
    docker exec -i contractor_clickhouse clickhouse-client --multiquery < infrastructure/docker/init_clickhouse.sql

### 4. Install Python dependencies
    cd services
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### 5. Run the pipeline
    # Terminal 1 — Start Temporal worker
    python -m pipeline.temporal.worker

    # Terminal 2 — Trigger pipeline
    python -m pipeline.temporal.scheduler

### 6. Start the API
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

### 7. Start the dashboard
    cd ../frontend
    npm install
    npm run dev
    # Open https://contractor-intel-five.vercel.app

---

## Pipeline Phases

**Phase 1: Discovery**
- Google Places API — 15+ IT businesses per city
- Playwright scraper — website content
- Hunter.io — email discovery (87% success rate)

**Phase 2: ML Scoring**
- 24 engineered features per business
- XGBoost classifier with cross-validation
- SHAP explainability per lead
- MLflow experiment tracking

**Phase 3: AI Agents**
- Research Agent — analyzes each business profile
- Email Agent — writes personalized outreach
- CrewAI orchestration with Groq inference

**Phase 4: Pipeline Automation**
- Temporal workflows — full orchestration
- Auto-retry on failure
- Scheduled runs across cities

**Phase 5: Feedback Loop**
- Track outreach outcomes (opened, replied, converted)
- Auto-retrain model when 10+ outcomes collected
- Model improves over time — real data flywheel

---

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Dashboard | https://contractor-intel-five.vercel.app | Next.js UI |
| API Docs | http://34.23.97.178:8001/docs | FastAPI Swagger |
| MLflow | http://34.23.97.178:5002 | Experiment tracking |
| Temporal UI | http://34.23.97.178:8888 | Workflow monitoring |
| Grafana | http://34.23.97.178:3001 | System monitoring |
| Prometheus | http://34.23.97.178:9090 | Metrics |
| Qdrant | http://34.23.97.178:6333/dashboard | Vector DB UI |

---

## Project Structure

    contractor-intelligence/
    services/
        discovery/          # Google Places + email finder
        scoring/            # XGBoost + SHAP + MLflow
        agents/             # CrewAI research + email agents
        api/                # FastAPI REST + GraphQL
        pipeline/
            temporal/       # Workflows + activities + worker
    frontend/               # Next.js dashboard
    infrastructure/
        docker/             # DB init scripts
        terraform/          # GCP IaC
    monitoring/             # Prometheus config
    data/
        models/             # Trained model artifacts
    docker-compose.yml      # 11 services

---

## The Self-Improving Loop

New businesses are discovered → ML model scores them → AI agents research and write personalized emails → outreach is sent and tracked → outcomes are recorded → model retrains on new data → better scores next time.

This feedback loop is what separates this from a simple scraper. The system gets smarter with every outreach cycle.

---

## Author

**Sakshi Chavan** — Software Engineer | Data Scientist | ML Engineer | New York, USA

GitHub: https://github.com/Sakshi3027
