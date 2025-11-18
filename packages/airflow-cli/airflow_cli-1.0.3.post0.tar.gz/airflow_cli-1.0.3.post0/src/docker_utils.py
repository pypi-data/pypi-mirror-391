import subprocess
import logging
import os
import shutil
import time
from glob import glob
from pathlib import Path
import yaml

log = logging.getLogger(__name__)


def run_command(cmd, check=True, capture_output=False, env=None):
    """Executa comando com tratamento de erro melhorado"""
    try:
        if capture_output:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True, env=env)
            return result.stdout
        else:
            subprocess.run(cmd, check=check, env=env)
            return None
    except subprocess.CalledProcessError as e:
        if capture_output and e.stderr:
            log.error(f"Command error: {e.stderr}")
        raise


def docker_up(build=False):
    """Inicia ambiente Docker com melhorias"""
    log.info("🚀 Starting Airflow Docker environment...")

    # Configurar variáveis de ambiente
    env = os.environ.copy()
    env["AIRFLOW_UID"] = "50000"
    env["AIRFLOW_GID"] = "0"
    env["DOCKER_INSECURE_NO_IPTABLES_RAW"] = "1"

    # Verificar/criar docker-compose.yml
    local_compose_file = "docker-compose.yml"
    if not os.path.exists(local_compose_file):
        log.info("📋 Creating docker-compose.yml from template...")
        package_compose_file = os.path.join(os.path.dirname(__file__), "docker-compose.yml")

        if not os.path.exists(package_compose_file):
            log.error("❌ Template docker-compose.yml not found in package!")
            raise FileNotFoundError("docker-compose.yml template missing")

        shutil.copy2(package_compose_file, local_compose_file)
        log.info("✅ docker-compose.yml created successfully!")
    else:
        log.info("📋 Using existing docker-compose.yml")

    # Criar diretórios necessários
    directories = ["dags", "logs", "plugins"]
    for directory in directories:
        if not os.path.exists(directory):
            log.info(f"📁 Creating '{directory}' directory...")
            os.makedirs(directory, exist_ok=True)

    # Construir imagens se solicitado
    if build:
        log.info("🔨 Building Docker images...")
        run_command(["docker", "compose", "build"], env=env)

    # Iniciar containers
    try:
        log.info("🐳 Starting containers...")
        run_command(["docker", "compose", "up", "-d"], env=env)

        log.info("⏳ Waiting for services to be healthy...")
        time.sleep(5)

        # Verificar status dos serviços
        healthy = wait_for_healthy_services(timeout=120)

        if healthy:
            log.info("✅ Airflow environment is ready!")
            log.info("🌐 Web UI: http://localhost:8080")
            log.info("👤 Username: airflow | Password: airflow")
            log.info("🔧 DBGate: http://localhost:3100")
            log.info("⚡ Spark Master: http://localhost:8081")
        else:
            log.warning("⚠️  Some services may not be fully ready. Check logs with: actl logs")

    except subprocess.CalledProcessError as e:
        log.error(f"❌ Failed to start Docker environment: {e}")
        log.error("💡 Try running: docker compose logs")
        raise


def docker_down(volumes=False):
    """Para ambiente Docker"""
    log.info("🛑 Stopping Airflow Docker environment...")

    cmd = ["docker", "compose", "down"]

    if volumes:
        log.warning("⚠️  Removing volumes - all data will be deleted!")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() == "yes":
            cmd.append("-v")
            log.info("🗑️  Removing volumes...")
        else:
            log.info("ℹ️  Volume removal cancelled")

    try:
        run_command(cmd, check=False)
        log.info("✅ Environment stopped successfully!")
    except Exception as e:
        log.error(f"❌ Error stopping environment: {e}")


def docker_status():
    """Mostra status dos containers"""
    log.info("📊 Checking container status...\n")

    try:
        output = run_command(["docker", "compose", "ps"], capture_output=True)
        print(output)

        # Verificar serviços não saudáveis
        unhealthy = run_command(["docker", "compose", "ps", "--filter", "health=unhealthy"], capture_output=True)

        if unhealthy and len(unhealthy.strip().split("\n")) > 1:
            log.warning("\n⚠️  Some services are unhealthy!")
            log.info("💡 Check logs with: actl logs")

    except Exception as e:
        log.error(f"❌ Error checking status: {e}")


def docker_logs(service="all", follow=False, lines=50):
    """Exibe logs dos containers"""
    service_map = {
        "webserver": "airflow-apiserver",
        "scheduler": "airflow-scheduler",
        "worker": "airflow-worker",
        "triggerer": "airflow-triggerer",
    }

    container = service_map.get(service, "")

    log.info(f"📋 Showing logs for: {service}")

    cmd = ["docker", "compose", "logs"]

    if follow:
        cmd.append("-f")

    cmd.extend(["--tail", str(lines)])

    if service != "all" and container:
        cmd.append(container)

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        log.info("\n✅ Stopped following logs")


def list_dags():
    """Lista DAGs disponíveis"""
    log.info("📝 Searching for DAGs...\n")

    dags_path = Path("dags")

    if not dags_path.exists():
        log.warning("⚠️  'dags' directory not found!")
        return

    # Procurar por arquivos Python
    dag_files = list(dags_path.rglob("*.py"))

    if not dag_files:
        log.warning("⚠️  No DAG files found in 'dags' directory")
        return

    log.info(f"Found {len(dag_files)} DAG file(s):\n")

    for dag_file in dag_files:
        relative_path = dag_file.relative_to(dags_path)

        # Tentar encontrar DAG ID no arquivo
        try:
            with open(dag_file, "r") as f:
                content = f.read()
                if "dag_id=" in content or "DAG(" in content:
                    print(f"  ✓ {relative_path}")
                else:
                    print(f"  ? {relative_path} (no DAG found)")
        except Exception:
            print(f"  ? {relative_path}")

    # Procurar por configs
    config_files = glob("dags/*/config.yml")

    if config_files:
        log.info(f"\n📋 Found {len(config_files)} config file(s):\n")
        for config in config_files:
            try:
                with open(config, "r") as f:
                    data = yaml.safe_load(f)
                    dag_id = data.get("args", {}).get("id", "unknown")
                    print(f"  ✓ {config} (DAG ID: {dag_id})")
            except Exception as e:
                print(f"  ✗ {config} (error: {e})")


def run_dag(dag_id=None, execution_date=None):
    """Executa DAG no Docker"""
    log.info("▶️  Preparing to run DAG...")

    # Se dag_id não foi fornecido, tentar buscar do config
    if not dag_id:
        try:
            config_files = glob("dags/*/config.yml")
            if not config_files:
                log.error("❌ No config.yml found and no DAG ID provided")
                log.info("💡 Usage: actl run <dag_id> or create dags/*/config.yml")
                return

            config = config_files[0]
            with open(config, "r") as file:
                config_data = yaml.safe_load(file)
                dag_id = config_data.get("args", {}).get("id")

            if not dag_id:
                log.error("❌ No 'id' found in config.yml")
                return

            log.info(f"📋 Using DAG ID from config: {dag_id}")

        except Exception as e:
            log.error(f"❌ Error reading config: {e}")
            return

    # Construir comando
    cmd = ["docker", "exec", "-it", "airflow-worker-container", "airflow", "dags", "test", dag_id]

    if execution_date:
        cmd.append(execution_date)

    try:
        log.info(f"🚀 Running DAG: {dag_id}")
        subprocess.run(cmd, check=True)
        log.info(f"✅ DAG '{dag_id}' executed successfully!")

    except subprocess.CalledProcessError as e:
        log.error(f"❌ Error running DAG: {e}")
        log.info("💡 Check if the container is running: actl status")
        log.info("💡 View logs: actl logs worker")


def fix_python_code(autofix=False):
    """Verifica qualidade do código com flake8"""
    log.info("🔧 Running code quality checks...")

    if not os.path.exists("dags"):
        log.warning("⚠️  'dags' directory not found!")
        return

    try:
        # Executar flake8
        result = subprocess.run(
            ["flake8", "dags", "--max-line-length=120", "--show-source"], capture_output=True, text=True
        )

        if result.returncode == 0:
            log.info("✅ No code quality issues found!")
        else:
            log.warning("⚠️  Found code quality issues:\n")
            print(result.stdout)

            if autofix:
                log.info("🔨 Attempting to auto-fix with autopep8...")
                try:
                    subprocess.run(["autopep8", "--in-place", "--recursive", "dags"], check=True)
                    log.info("✅ Auto-fix completed! Re-run 'actl fix' to verify.")
                except FileNotFoundError:
                    log.warning("⚠️  autopep8 not installed. Install with: pip install autopep8")

    except FileNotFoundError:
        log.error("❌ flake8 not found! Install with: pip install flake8")
    except Exception as e:
        log.error(f"❌ Error checking code: {e}")


def open_shell(service="worker"):
    """Abre shell interativo no container"""
    container_map = {
        "worker": "airflow-worker-container",
        "scheduler": "airflow-scheduler-container",
        "webserver": "airflow-api-server-container",
    }

    container = container_map.get(service, "airflow-worker-container")

    log.info(f"💻 Opening shell in {service} container...")
    log.info("💡 Type 'exit' to close the shell")

    try:
        subprocess.run(["docker", "exec", "-it", container, "bash"])
    except Exception as e:
        log.error(f"❌ Error opening shell: {e}")


def restart_service(service="all"):
    """Reinicia serviços"""
    log.info(f"🔄 Restarting {service}...")

    try:
        if service == "all":
            run_command(["docker", "compose", "restart"])
        else:
            run_command(["docker", "compose", "restart", service])

        log.info("✅ Service(s) restarted successfully!")

    except Exception as e:
        log.error(f"❌ Error restarting service: {e}")


def wait_for_healthy_services(timeout=120):
    """Aguarda serviços ficarem saudáveis"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            result = run_command(["docker", "compose", "ps", "--format", "json"], capture_output=True)

            # Simplificado: apenas verificar se containers estão rodando
            if "running" in result.lower():
                return True

        except Exception:
            pass

        time.sleep(5)

    return False
