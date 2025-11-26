# Airflow
 Airflow repository projects 

# Airflow ETL Pipelines

![Airflow Developer Flow](https://datageeklab.com/wp-content/uploads/2024/04/airflow-developer-flow.gif)

A production-ready Apache Airflow setup running on Docker with multiple ETL pipelines for weather data and cryptocurrency analytics. This repository demonstrates orchestration best practices, TaskFlow API usage, and distributed task execution with CeleryExecutor.

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+
- At least 4GB RAM allocated to Docker
- Python 3.12+ (for local DAG testing)

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Airflow
   ```

2. **Start the Airflow cluster**
   ```bash
   docker-compose up -d
   ```

3. **Access the Airflow UI**
   - Navigate to: http://localhost:8080
   - **Username**: `airflow`
   - **Password**: `airflow`

4. **Monitor services health**
   ```bash
   docker-compose ps
   ```

5. **Stop the cluster**
   ```bash
   docker-compose down
   # To remove volumes as well:
   docker-compose down -v
   ```

---

## 📊 Available Pipelines

### 1. Weather ETL Pipeline
**Files**: `01-ETLWeatherPrint.py`, `02-ETLWeatherPostgres.py`, `03-ETLWeatherPostgresAndPrint.py`

Extracts weather data from external APIs, transforms it, and loads into PostgreSQL database.

**Features**:
- Real-time weather data extraction
- Data validation and transformation
- PostgreSQL integration
- Error handling and retries

### 2. Cryptocurrency Pipeline
**File**: `CriptoPipeline.py`

Fetches cryptocurrency prices from Coinlore API and processes Bitcoin data.

**Pipeline Flow**:
```
Extract → Transform → Load
   ↓          ↓         ↓
 API Call  Filter BTC  Print/Store
```

**Tasks**:
- `extract`: Calls Coinlore API for crypto tickers
- `transform`: Filters Bitcoin (ID: 90) from response
- `load`: Outputs processed data

---

## 🏗️ Architecture

### Services Overview

| Service | Purpose | Port |
|---------|---------|------|
| **postgres** | Metadata database | 5432 |
| **redis** | Message broker for Celery | 6379 |
| **airflow-apiserver** | Web UI & REST API | 8080 |
| **airflow-scheduler** | Orchestrates DAG execution | - |
| **airflow-dag-processor** | Parses and validates DAGs | - |
| **airflow-worker** | Executes tasks | - |
| **airflow-triggerer** | Handles deferrable tasks | - |

### Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Airflow Cluster                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 /dags  →  🔍 dag-processor  →  📅 scheduler             │
│                                         ↓                    │
│                                    🔴 redis (queue)          │
│                                         ↓                    │
│                                    👷 worker (execute)       │
│                                         ↓                    │
│                                    💾 postgres (store)       │
│                                         ↓                    │
│                                    🌐 UI (display)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Airflow/
├── config/
│   └── airflow.cfg              # Airflow configuration
├── dags/                        # 🎯 Your DAG files go here
│   ├── __pycache__/            # Python compiled files
│   ├── CriptoPipeline.py       # Crypto ETL pipeline
│   ├── 01-ETLWeatherPrint.py   # Weather pipeline v1
│   ├── 02-ETLWeatherPostgres.py # Weather pipeline v2
│   ├── 03-ETLWeatherPostgresAndPrint.py # Weather pipeline v3
│   ├── SimpleHTTPOperator.py   # Custom HTTP operator
│   └── transformer.py          # Utility functions
├── logs/                        # Execution logs
│   ├── dag_id=<dag_name>/      # Logs per DAG
│   │   └── run_id=<execution>/ # Logs per run
│   │       └── task_id=<task>/ # Logs per task
│   └── dag_processor/          # DAG parsing logs
├── plugins/                     # Custom Airflow plugins
├── images/                      # Documentation images
├── docker-compose.yaml         # 🐳 Docker services definition
└── README.md                   # This file
```

### Key Directories

- **`/dags`**: Place your DAG files here. Auto-scanned every 30 seconds.
- **`/logs`**: Task execution logs. Critical for debugging.
- **`/config`**: Airflow settings (executors, pools, parallelism).
- **`/plugins`**: Custom operators, hooks, sensors, and macros.

---

## 🛠️ Technologies Used

### Core Stack
- **Apache Airflow 3.1.3**: Workflow orchestration platform
- **Python 3.12**: DAG development language
- **PostgreSQL 16**: Metadata and data storage
- **Redis 7.2**: Message broker for distributed execution
- **Docker & Docker Compose**: Containerization

### Python Libraries
- `requests`: HTTP client for API calls
- `pendulum`: Timezone-aware datetime handling
- `json`: Data serialization

### Airflow Components
- **CeleryExecutor**: Distributed task execution
- **TaskFlow API**: Modern Python-based DAG authoring
- **XCom**: Inter-task communication

---

## 💡 Key Concepts Demonstrated

### 1. TaskFlow API (Modern DAG Authoring)
```python
from airflow.decorators import dag, task

@dag(schedule_interval='@daily', catchup=False)
def my_pipeline():
    
    @task()
    def extract():
        return data
    
    @task()
    def transform(data):
        return processed_data
    
    @task()
    def load(processed_data):
        save_to_db(processed_data)
    
    # Implicit dependencies through function calls
    data = extract()
    processed = transform(data)
    load(processed)

dag_instance = my_pipeline()
```

### 2. Task Dependencies
```python
# Method 1: TaskFlow (implicit via arguments)
result_a = task_a()
result_b = task_b(result_a)  # task_b waits for task_a

# Method 2: Traditional (explicit with >>)
task1 >> task2 >> task3  # Sequential: 1 → 2 → 3
[task1, task2] >> task3  # Parallel: (1, 2) → 3
```

### 3. XCom (Cross-Communication)
- Automatically stores `return` values from `@task()` functions
- Retrieves values when passed as arguments to downstream tasks
- **Limit**: 48KB in PostgreSQL backend
- For large data: use external storage (S3, GCS) and pass references

### 4. Scheduling Strategies
```python
schedule_interval=None           # Manual trigger only
schedule_interval='@daily'       # Every day at midnight
schedule_interval='@hourly'      # Every hour
schedule_interval='0 9 * * *'    # Cron: Daily at 9 AM
schedule_interval=timedelta(hours=2)  # Every 2 hours
```

### 5. Idempotency
All pipelines are designed to be idempotent:
- Running twice produces the same result
- Safe for retries and backfills
- Uses upserts and transaction IDs

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Airflow User
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=your_secure_password

# Additional Python Packages
_PIP_ADDITIONAL_REQUIREMENTS=requests pandas sqlalchemy

# Airflow Settings
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
```

### Adding Python Dependencies

**Method 1: Environment Variable (Quick)**
```yaml
# In docker-compose.yaml
_PIP_ADDITIONAL_REQUIREMENTS: requests pandas numpy
```

**Method 2: Custom Docker Image (Production)**
```dockerfile
FROM apache/airflow:3.1.3
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

---

## 📚 Useful Commands

### Docker Management
```bash
# View logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-worker

# Restart services
docker-compose restart

# Execute Airflow CLI commands
docker-compose exec airflow-scheduler airflow dags list
docker-compose exec airflow-scheduler airflow tasks list <dag_id>

# Access PostgreSQL
docker-compose exec postgres psql -U airflow
```

### DAG Operations
```bash
# Test a DAG (without affecting schedule)
docker-compose exec airflow-scheduler airflow dags test <dag_id> 2025-01-12

# Trigger a DAG manually
docker-compose exec airflow-scheduler airflow dags trigger <dag_id>

# Pause/Unpause a DAG
docker-compose exec airflow-scheduler airflow dags pause <dag_id>
docker-compose exec airflow-scheduler airflow dags unpause <dag_id>

# Backfill historical runs
docker-compose exec airflow-scheduler airflow dags backfill <dag_id> \
  --start-date 2025-01-01 --end-date 2025-01-31
```

### Debugging
```bash
# Check DAG parsing errors
# Go to UI → Browse → Import Errors

# View task logs
# logs/dag_id=<name>/run_id=<execution>/task_id=<task>/attempt=1.log

# Validate DAG syntax
python3 dags/CriptoPipeline.py
```

---

## 🎯 Best Practices Implemented

✅ **Idempotent Tasks**: All tasks can run multiple times safely  
✅ **Error Handling**: Retry logic with exponential backoff  
✅ **Logging**: Comprehensive logging for debugging  
✅ **Modularity**: Reusable functions in separate modules  
✅ **Type Hints**: Better code documentation and IDE support  
✅ **TaskFlow API**: Modern, Pythonic DAG authoring  
✅ **Version Control**: All DAGs and configs in Git  
✅ **Documentation**: Docstrings for all functions  

---

## 🔒 Security Notes

- Default credentials (`airflow/airflow`) are for **develop
