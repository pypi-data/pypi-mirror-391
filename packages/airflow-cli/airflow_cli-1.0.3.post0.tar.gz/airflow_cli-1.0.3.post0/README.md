# 🚀 Airflow Docker CLI

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

**A powerful command-line tool to manage Apache Airflow environments using Docker**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Commands](#-commands) • [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

- 🐳 **Easy Setup**: Launch a complete Airflow environment with a single command
- 🎯 **Developer Friendly**: Hot-reload DAGs, instant testing, and debugging tools
- 📦 **Pre-configured Stack**: PostgreSQL, Redis, MongoDB, Spark, and DBGate included
- 🔧 **Built-in Tools**: Code linting, DAG validation, and interactive shell access
- 📊 **Monitoring**: Quick status checks and log viewing
- 🎨 **Beautiful CLI**: Colorful output with emojis and clear status indicators
- 🔄 **Multiple Workers**: Celery executor with configurable Spark workers

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7+** - [Download](https://www.python.org/downloads/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
  - Docker Engine 20.10+
  - Docker Compose v2+
- **Git** (optional) - For version control

### System Requirements

- **RAM**: Minimum 4GB available (8GB+ recommended)
- **Disk Space**: At least 10GB free
- **OS**: Linux, macOS, or Windows with WSL2

## 🚀 Installation

### From PyPI (Recommended)

```bash
pip install airflow-cli
```

### From Source

```bash
# Clone the repository
git clone https://github.com/lema-ufpb/airflow-cli.git
cd airflow-cli

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
actl --help
```

You should see the CLI help menu with available commands.

## ⚡ Quick Start

### 1. Initialize Airflow Environment

```bash
actl up
```

This command will:

- ✅ Check Docker installation and requirements
- ✅ Create `docker-compose.yml` configuration
- ✅ Set up directory structure (`dags/`, `logs/`, `plugins/`)
- ✅ Start all Airflow services
- ✅ Initialize the Airflow database
- ✅ Create admin user

**First startup may take 2-3 minutes** while Docker pulls images and initializes services.

### 2. Access the Airflow UI

Once started, open your browser:

🌐 **Airflow Web UI**: http://localhost:8080

- **Username**: `airflow`
- **Password**: `airflow`

🔧 **DBGate** (Database UI): http://localhost:3100

⚡ **Spark Master UI**: http://localhost:8080 (on port 8081 internally)

### 3. Check Status

```bash
actl status
```

### 4. Create Your First DAG

Create a DAG file in the `dags/` directory:

```python
# dags/my_first_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'my_first_dag',
    default_args=default_args,
    description='My first Airflow DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    task1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    task2 = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hello from Airflow!"',
    )

    task1 >> task2
```

### 5. Test Your DAG

```bash
# List available DAGs
actl list

# Run a specific DAG
actl run my_first_dag

# Or use config.yml structure
# dags/my_first_dag/config.yml
actl run
```

### 6. Stop the Environment

```bash
# Stop services (keeps data)
actl down

# Stop and remove all data
actl down --volumes
```

## 📖 Commands

### Core Commands

| Command        | Description                   | Example                  |
| -------------- | ----------------------------- | ------------------------ |
| `actl up`      | Start the Airflow environment | `actl up --build`        |
| `actl down`    | Stop the environment          | `actl down --volumes`    |
| `actl status`  | Check service health          | `actl status`            |
| `actl restart` | Restart services              | `actl restart scheduler` |

### Development Commands

| Command      | Description             | Example                       |
| ------------ | ----------------------- | ----------------------------- |
| `actl list`  | List available DAGs     | `actl list`                   |
| `actl run`   | Execute a DAG           | `actl run my_dag`             |
| `actl fix`   | Run code quality checks | `actl fix --autofix`          |
| `actl shell` | Open interactive shell  | `actl shell --service worker` |

### Monitoring Commands

| Command            | Description         | Example                   |
| ------------------ | ------------------- | ------------------------- |
| `actl logs`        | View container logs | `actl logs scheduler -f`  |
| `actl logs -n 100` | Show last 100 lines | `actl logs worker -n 100` |

---

## 🎯 Detailed Command Reference

### `actl up`

Start the complete Airflow environment.

```bash
# Basic startup
actl up

# Rebuild images before starting
actl up --build
```

**What it does:**

- Creates necessary directories
- Copies docker-compose.yml if missing
- Starts all containers (postgres, redis, airflow components, spark, mongo)
- Waits for services to become healthy
- Displays access URLs

### `actl down`

Stop the Airflow environment.

```bash
# Stop services (preserve data)
actl down

# Stop and remove volumes (⚠️ deletes all data!)
actl down --volumes
```

### `actl status`

Display the current status of all containers.

```bash
actl status
```

Shows:

- Container names
- Status (running/stopped/unhealthy)
- Ports
- Health check status

### `actl logs`

View logs from containers.

```bash
# View all logs (last 50 lines)
actl logs

# Follow logs in real-time
actl logs scheduler -f

# View specific service logs
actl logs worker -n 200

# Available services: webserver, scheduler, worker, triggerer, all
```

### `actl run`

Execute a DAG for testing.

```bash
# Run DAG by ID
actl run my_dag_id

# Run with specific execution date
actl run my_dag_id --date 2024-01-01

# Auto-detect from config.yml
actl run
```

**Config File Structure:**

```yaml
# dags/my_dag/config.yml
args:
  id: "my_dag_id"
```

### `actl list`

List all DAGs found in the dags directory.

```bash
actl list
```

Shows:

- Python files containing DAGs
- Config files with DAG IDs
- Relative paths

### `actl fix`

Run code quality checks with flake8.

```bash
# Check code quality
actl fix

# Auto-fix issues (requires autopep8)
actl fix --autofix
```

### `actl shell`

Open an interactive bash shell in a container.

```bash
# Open shell in worker container (default)
actl shell

# Open shell in specific service
actl shell --service scheduler

# Available services: worker, scheduler, webserver
```

**Useful inside shell:**

```bash
# List DAGs
airflow dags list

# Test a task
airflow tasks test my_dag my_task 2024-01-01

# Check connections
airflow connections list
```

### `actl restart`

Restart services without full shutdown.

```bash
# Restart all services
actl restart

# Restart specific service
actl restart scheduler
```

---

## 🏗️ Architecture

The CLI sets up the following services:

```
┌─────────────────────────────────────────────────────┐
│                  Docker Environment                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Airflow    │  │   Airflow    │  │  Airflow  │ │
│  │  Web Server  │  │   Scheduler  │  │  Worker   │ │
│  │  (Port 8080) │  │              │  │  (Celery) │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                │
│  │   Airflow    │  │   Airflow    │                │
│  │   Triggerer  │  │DAG Processor │                │
│  └──────────────┘  └──────────────┘                │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │  MongoDB  │ │
│  │  (Port 5432) │  │  (Port 6379) │  │(Port 27017│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                │
│  │Spark Master  │  │ Spark Workers│                │
│  │  (Port 7077) │  │   (2 nodes)  │                │
│  └──────────────┘  └──────────────┘                │
│                                                       │
│  ┌──────────────┐                                    │
│  │   DBGate     │  Database Management UI           │
│  │  (Port 3100) │                                    │
│  └──────────────┘                                    │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 🗂️ Directory Structure

```
your-project/
├── dags/                    # Your DAG files
│   ├── my_dag/
│   │   ├── config.yml      # DAG configuration
│   │   └── dag.py          # DAG definition
│   └── another_dag.py
├── logs/                    # Airflow logs (auto-created)
├── plugins/                 # Airflow plugins (auto-created)
├── data/                    # Shared data directory
└── docker-compose.yml       # Docker configuration (auto-created)
```

---

## 🐛 Troubleshooting

### Docker Not Running

**Error:** `❌ Docker daemon is not running!`

**Solution:**

- **Linux**: `sudo systemctl start docker`
- **macOS/Windows**: Start Docker Desktop application

### Port Already in Use

**Error:** `⚠️ Port 8080 is already in use`

**Solution:**

1. Find process using the port:

   ```bash
   # Linux/macOS
   lsof -i :8080

   # Windows
   netstat -ano | findstr :8080
   ```

2. Stop the process or modify `docker-compose.yml` to use different ports

### Services Unhealthy

**Error:** `⚠️ Some services are unhealthy!`

**Solution:**

```bash
# Check logs
actl logs scheduler
actl logs worker

# Restart services
actl restart

# Full reset (⚠️ removes data)
actl down --volumes
actl up
```

### DAG Not Appearing

**Issues:**

- DAG file not in `dags/` directory
- Python syntax errors
- DAG paused by default

**Solution:**

```bash
# Check DAG list
actl list

# Validate DAG syntax
actl fix

# Check logs
actl logs scheduler -f

# Open shell and check
actl shell
airflow dags list
```

### Permission Denied (Linux)

**Error:** `permission denied while connecting to Docker`

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker ps
```

### Low Disk Space

**Error:** System slow or containers failing

**Solution:**

```bash
# Clean Docker system
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

---

## 🔧 Advanced Usage

### Custom Docker Compose

You can modify the generated `docker-compose.yml` to:

- Change resource limits
- Add custom environment variables
- Configure different executors
- Add new services

### Environment Variables

Create a `.env` file:

```bash
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=secure_password
AIRFLOW_VAR_MY_VARIABLE=value
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Apache Airflow team for the amazing orchestration platform
- Docker team for containerization
- LEMA-UFPB for development and maintenance

---

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/lema-ufpb/airflow-cli/issues)
- 📖 Documentation: [Official Docs](https://github.com/lema-ufpb/airflow-cli)

---

<div align="center">

⭐ Star us on GitHub — it helps!

</div>
