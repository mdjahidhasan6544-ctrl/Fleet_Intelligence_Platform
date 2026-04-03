# Gemini CLI Project Mandates - Fleet Tracking

This file contains project-specific instructions and context for Gemini CLI agents.

## Project Overview
The **Fleet Tracking System** is a real-time monitoring platform for vehicle telemetry (GPS, speed, fuel). It uses a distributed architecture with Django, Celery, Redis, and PostgreSQL.

## Core Mandates

### 1. Data Ingestion & Real-time Flow
- **Redis First**: Telemetry is first pushed to Redis (`raw_device_data` list). Background Celery workers (`process_ingestion_queue`) process this data, update real-time states in Redis (`device_state:<id>`), and then bulk-save to PostgreSQL.
- **Alerts**: Alerts are pushed to the `alerts` list in Redis for immediate UI updates.
- **Geofencing**: The LA geofence center (34.0522, -118.2437) is hardcoded in `tracking/tasks.py`. Do not change without user instruction.

### 2. Authentication
- All device ingestion requests MUST include an `X-API-Key` header.
- Middleware (`tracking/middleware.py`) handles `Device` identification based on this key.

### 3. Background Tasks
- **In-memory Processing**: Prioritize Redis for low-latency operations (live tracking, alerts).
- **Scheduled Tasks**: Hourly and daily aggregations are handled by Celery Beat. Ensure `celery_beat` service is running during development.

### 4. Testing & Simulation
- **Simulation**: Use `simulate.py` for manual testing and data generation.
- **Verification**: Always run `pytest` and `python validate_ui.py` after structural changes to ensure both the API and the map dashboard remain functional.

## Tech Stack Constants
- **Database**: PostgreSQL (Docker service: `db`)
- **Queue/Cache**: Redis (Docker service: `redis`)
- **Frontend**: Leaflet.js (Map), Vanilla JS (Sidebar/Alerts)
- **Backend**: Django 6.0+, DRF

## Development Workflow
- Always verify changes against the Dockerized environment (`docker-compose up`).
- When modifying models, ensure migrations are generated and applied.
- Maintain the separation between real-time data (Redis) and historical data (PostgreSQL).
