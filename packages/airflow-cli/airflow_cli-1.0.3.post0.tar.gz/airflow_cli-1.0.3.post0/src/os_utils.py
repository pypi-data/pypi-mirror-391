import logging
import subprocess
import sys
import platform

log = logging.getLogger(__name__)


def check_docker():
    """Verifica se Docker está instalado e rodando com feedback detalhado"""

    # Verificar versão do Docker
    try:
        docker_version = subprocess.check_output(["docker", "--version"], stderr=subprocess.STDOUT, text=True).strip()
        log.info(f"✅ Docker found: {docker_version}")
    except FileNotFoundError:
        log.error("❌ Docker is not installed!")
        log.info("💡 Install Docker from: https://docs.docker.com/get-docker/")
        return False
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Docker check failed: {e.output}")
        return False

    # Verificar se Docker daemon está rodando
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT, text=True)
        log.info("✅ Docker daemon is running")
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Docker daemon is not running!: {e}")

        system = platform.system()
        if system == "Linux":
            log.info("💡 Try: sudo systemctl start docker")
        elif system == "Darwin":  # macOS
            log.info("💡 Start Docker Desktop application")
        elif system == "Windows":
            log.info("💡 Start Docker Desktop application")

        return False
    except Exception as e:
        log.error(f"❌ Error checking Docker daemon: {e}")
        return False

    # Verificar Docker Compose
    try:
        compose_version = subprocess.check_output(
            ["docker", "compose", "version"], stderr=subprocess.STDOUT, text=True
        ).strip()
        log.info(f"✅ Docker Compose found: {compose_version}")
    except FileNotFoundError:
        log.error("❌ Docker Compose is not available!")
        log.info("💡 Docker Compose should be included with Docker Desktop")
        log.info("💡 For Linux: https://docs.docker.com/compose/install/")
        return False
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Docker Compose check failed: {e.output}")
        return False

    # Verificar permissões (especialmente no Linux)
    if platform.system() == "Linux":
        try:
            subprocess.check_output(["docker", "ps"], stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            if "permission denied" in e.output.lower():
                log.error("❌ Permission denied accessing Docker!")
                log.info("💡 Add your user to docker group:")
                log.info("   sudo usermod -aG docker $USER")
                log.info("   Then logout and login again")
                return False

    log.info("✅ All Docker checks passed!")
    return True


def check_system_requirements():
    """Verifica requisitos do sistema"""
    log.info("🔍 Checking system requirements...")

    # Verificar Python
    python_version = sys.version.split()[0]
    log.info(f"🐍 Python version: {python_version}")

    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 7):
        log.warning(f"⚠️  Python {major}.{minor} detected. Python 3.7+ recommended")
    else:
        log.info("✅ Python version is compatible")

    # Verificar sistema operacional
    system = platform.system()
    log.info(f"💻 Operating System: {system} {platform.release()}")

    # Verificar espaço em disco (simplificado)
    try:
        import shutil

        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)

        if free_gb < 10:
            log.warning(f"⚠️  Low disk space: {free_gb}GB free. Recommend at least 10GB")
        else:
            log.info(f"✅ Disk space: {free_gb}GB available")
    except Exception:
        log.debug("Could not check disk space")

    return True


def check_ports():
    """Verifica se portas necessárias estão disponíveis"""
    import socket

    required_ports = {
        8080: "Airflow Web UI",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        3100: "DBGate",
        7077: "Spark Master",
    }

    log.info("🔌 Checking required ports...")

    ports_in_use = []

    for port, service in required_ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()

        if result == 0:
            ports_in_use.append((port, service))
            log.warning(f"⚠️  Port {port} ({service}) is already in use")
        else:
            log.debug(f"✅ Port {port} ({service}) is available")

    if ports_in_use:
        log.warning("\n⚠️  Some ports are already in use!")
        log.info("💡 Stop services using these ports or modify docker-compose.yml")
        return False

    log.info("✅ All required ports are available")
    return True
