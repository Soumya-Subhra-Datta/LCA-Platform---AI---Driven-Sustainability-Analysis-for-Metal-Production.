# LCA Platform

AI-Driven Life Cycle Assessment Platform for Sustainable Metal Production

## Overview

An end-to-end web application integrating Machine Learning, Explainable AI, Life Cycle Assessment, and Circular Economy analysis for the mining and metallurgy domain. Built with FastAPI, scikit-learn, and a modern responsive dashboard.

## Quick Start

```bash
# 1. Clone and navigate to the project
cd lca_platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment config
cp .env.example .env

# 5. Setup database and train models
python scripts/setup_project.py all

# 6. Start the application
python run.py
```

Open http://localhost:8000 in your browser.

## Project Structure

```
lca_platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # SQLAlchemy database setup
│   │   ├── models/              # Database ORM models
│   │   │   ├── user.py          # User authentication
│   │   │   ├── dataset.py       # Dataset metadata
│   │   │   ├── prediction.py    # ML predictions
│   │   │   ├── environmental.py # LCA metrics
│   │   │   ├── circularity.py   # Circularity metrics
│   │   │   ├── sustainability.py# Sustainability scores
│   │   │   ├── report.py        # Generated reports
│   │   │   └── audit.py         # Audit logging
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── api/v1/              # API route handlers
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── datasets.py      # Dataset management
│   │   │   ├── predictions.py   # ML prediction endpoints
│   │   │   ├── environmental.py # LCA assessment endpoints
│   │   │   ├── circularity.py   # Circular economy endpoints
│   │   │   ├── reports.py       # Report generation
│   │   │   └── dashboard.py     # Dashboard data
│   │   ├── services/            # Business logic layer
│   │   ├── pipeline/            # Data loading and preprocessing
│   │   │   ├── data_loader.py   # Loads all 15 datasets
│   │   │   ├── preprocessor.py  # Cleaning, imputation, encoding
│   │   │   └── feature_engineering.py # Feature creation
│   │   ├── ml/                  # Machine Learning
│   │   │   ├── models/base.py   # 4 trained models
│   │   │   └── explainability/  # SHAP integration
│   │   ├── lca/                 # Life Cycle Assessment engine
│   │   │   └── engine.py        # Carbon, water, energy, waste
│   │   ├── circular/            # Circular economy engine
│   │   │   └── engine.py        # Circularity & sustainability
│   │   └── utils/               # Security, validation, logging
│   ├── frontend/                # Dashboard UI
│   │   ├── index.html           # Single-page application
│   │   ├── css/style.css        # Responsive styles
│   │   └── js/                  # JavaScript modules
│   ├── tests/                   # Test suite
│   └── models/                  # Saved model artifacts
├── scripts/                     # Setup and training scripts
├── alembic/                     # Database migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py                       # Application entry point
```

## Features

### AI/ML Pipeline
- **HREE Percentage Predictor** (Gradient Boosting) - Predicts heavy rare earth element content
- **Deposit Type Classifier** (Random Forest) - Classifies geological deposit types
- **Resource Size Estimator** (Random Forest) - Estimates resource tonnage from grade/composition
- **Dy2O3 Content Predictor** (Gradient Boosting) - Predicts critical dysprosium content
- **SHAP Explainability** - Natural language explanations for every prediction

### LCA Engine
- Carbon footprint estimation (mining, processing, transport)
- Water footprint analysis
- Energy consumption modeling
- Waste generation calculation
- Acidification and eutrophication impact assessment
- Environmental impact scoring (A-E grades)

### Circular Economy
- Circularity scoring (0-100)
- Recycling potential assessment
- Resource efficiency metrics
- Waste diversion analysis
- Actionable sustainability recommendations

### Dashboard
- Interactive charts (Chart.js)
- Real-time data visualization
- Dataset exploration
- Model performance monitoring
- LCA results visualization
- Sustainability radar charts

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and receive JWT |
| GET | `/api/v1/datasets/` | List all datasets |
| GET | `/api/v1/datasets/{name}` | Dataset details |
| GET | `/api/v1/datasets/{name}/sample` | Sample data |
| POST | `/api/v1/predictions/train` | Train all models |
| POST | `/api/v1/predictions/predict` | Run prediction |
| GET | `/api/v1/predictions/metrics` | Model metrics |
| POST | `/api/v1/environmental/assess` | Run LCA assessment |
| GET | `/api/v1/environmental/benchmarks` | Industry benchmarks |
| POST | `/api/v1/circularity/calculate` | Circularity analysis |
| POST | `/api/v1/circularity/sustainability` | Sustainability score |
| POST | `/api/v1/reports/generate` | Generate report |
| GET | `/api/v1/dashboard/` | Dashboard data |
| GET | `/health` | Health check |

Full interactive docs at `/docs` (Swagger UI).

## Datasets

15 datasets covering:
- **REE Mining Projects** - 146 projects with 15 REE oxide compositions
- **REE Processing Facilities** - 67 facilities with supply chain data
- **Open Mining Database** - 2,413 facilities with production, waste, transport, processing data
- **World Mining Commodities** - 169 countries, 65 commodities

## Configuration

Environment variables (`.env`):
- `DATABASE_URL` - SQLite (dev) or MySQL (prod)
- `APP_SECRET_KEY` - JWT signing key
- `MODEL_DIR` - Where trained models are saved
- `LOG_LEVEL` - Logging verbosity

## Testing

```bash
cd lca_platform
python -m pytest backend/tests/ -v
```

## Docker

```bash
docker-compose up --build
```

## AWS Deployment

The platform is ready for AWS Free Tier deployment:
- **EC2** - Run the Docker container
- **RDS** - MySQL database
- **S3** - Model artifact storage
- **Route 53** - DNS configuration

See `.env.example` for AWS-specific configuration.

## License

Internal project - all rights reserved.
