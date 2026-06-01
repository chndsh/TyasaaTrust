# TyasaaTrust

## Introduction
TyasaaTrust is a trust-scoring platform that combines social graph signals, psychometric inputs, and behavioral data into a unified score for merchants. The repository contains a FastAPI backend with modular scoring components and a Streamlit frontend for exploration and demo workflows. Supporting services (PostgreSQL and Redis) are provisioned with Docker Compose, and mock data tooling is included for local development.

## Objectives
- Provide a modular trust-scoring pipeline with independent components for social, psychometric, and behavioral signals.
- Expose scoring and ingestion capabilities through a FastAPI API with documented routes.
- Deliver a Streamlit UI for exploring graphs, quizzes, and dashboards during demos.
- Support local development with Docker Compose services and a single consolidated Python dependency set.
- Enable repeatable mock data generation for demos and testing.

## Architecture
### High-level flow
- Streamlit UI (`frontend/`) calls the FastAPI service (`backend/`).
- FastAPI routes invoke module logic in `backend/modules/` and persist results using PostgreSQL.
- Background tasks are orchestrated with Celery using Redis as the broker.

### Repository layout
- `backend/`: FastAPI app, routers, scoring modules, Celery tasks, and database schema.
- `frontend/`: Streamlit app and UI pages.
- `backend/db/init.sql`: Database schema for PostgreSQL.
- `backend/data/`: Mock data generation utilities.
- `docker-compose.yml`: Local PostgreSQL and Redis services.
- `requirements.txt`: Consolidated Python dependencies for backend and frontend.
- `.env.example`: Environment variable template for local configuration.
