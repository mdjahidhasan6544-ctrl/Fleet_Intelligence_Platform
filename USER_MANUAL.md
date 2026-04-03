# Fleet Tracking System - User Manual

Welcome to the **Fleet Tracking System**, a real-time monitoring platform for vehicle telemetry (GPS, speed, fuel). This manual provides instructions on how to set up, run, and test the project.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Docker & Docker Compose**: (Recommended) For running the entire stack (Postgres, Redis, Celery, Django).
- **Python 3.12+**: If you intend to run simulations or validation scripts locally.
- **Node.js**: (Optional) For frontend development, though the current UI uses Vanilla JS and Leaflet.js.

---

## 2. Quick Start (Docker Compose)

The easiest way to get the system running is using Docker.

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd fleet-tracking
    ```

2.  **Start the Services**:
    ```bash
    docker-compose up --build
    ```
    This command will build and start:
    - `db`: PostgreSQL database.
    - `redis`: Redis for caching, queuing, and real-time state.
    - `web`: The Django application (Gunicorn/Runserver).
    - `celery_worker`: Background task processor for data ingestion and alerts.
    - `celery_beat`: Scheduler for periodic data aggregation.

3.  **Run Migrations**:
    Open a new terminal and run:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

---

## 3. Configuration

The application uses environment variables for configuration. While the `docker-compose.yml` provides defaults, you can override them by creating a `.env` file in the root directory.

**Key Settings (in `fleet_project/settings.py`):**
- `DATABASE_URL`: Connection string for PostgreSQL.
- `CELERY_BROKER_URL`: Connection string for Redis (e.g., `redis://redis:6379/0`).
- `SECRET_KEY`: Django secret key.

---

## 4. Initial Data Setup

To see data on the dashboard, you must first create a `Device` in the system.

1.  **Create a Superuser**:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to set a username and password.

2.  **Add a Device**:
    - Navigate to `http://localhost:8000/admin` and log in.
    - Click on **Devices** > **Add Device**.
    - Set the **API Key** to `test-key-123` (this matches the default in `simulate.py`).
    - Give it a name (e.g., "Truck 01") and save.

---

## 5. Running the Simulator

To simulate real-time telemetry ingestion without a physical device:

1.  **Install dependencies** (if not already installed):
    ```bash
    pip install requests
    ```

2.  **Run the script**:
    ```bash
    python simulate.py
    ```
    The script will start sending random GPS coordinates, speed, and fuel data to the local API. You should see `Sent: 202` in your terminal.

---

## 6. Monitoring the Dashboard

Once the services are running and the simulator is active:

1.  **Open the Map**: Navigate to `http://localhost:8000`.
2.  **Live Tracking**: You will see a vehicle marker moving on the map in real-time.
3.  **Sidebar**:
    - **Device List**: Shows the current status (Speed, Fuel) of all active devices.
    - **Alerts**: Displays real-time notifications for:
        - **Overspeeding** (> 100 km/h)
        - **Fuel Theft** (> 10% drop)
        - **Geofencing** (Leaving/Entering LA Central Zone)

---

## 7. Testing & Validation

### Automated Tests
Run the suite of backend tests:
```bash
pytest
```

### UI Validation
To verify the UI and end-to-end flow (requires Playwright):
1.  **Install Playwright**:
    ```bash
    pip install playwright
    playwright install chromium
    ```
2.  **Run Validation**:
    ```bash
    python validate_ui.py
    ```

---

## 8. Troubleshooting

- **Redis Connection Error**: Ensure the `redis` service is running (`docker-compose ps`).
- **No Data on Map**:
    - Verify the `X-API-Key` in `simulate.py` matches the `api_key` of a Device in the Django admin.
    - Check Celery logs: `docker-compose logs celery_worker`.
- **Database Migrations**: If you see errors about missing tables, ensure you ran `python manage.py migrate`.

---

*For further assistance, please contact the development team.*
