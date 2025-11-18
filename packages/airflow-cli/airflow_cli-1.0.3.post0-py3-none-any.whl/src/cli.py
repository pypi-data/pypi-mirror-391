import argparse
import logging
import sys
from .os_utils import check_docker
from .docker_utils import docker_up, docker_down, run_dag, fix_python_code, docker_status, docker_logs, list_dags


class ColoredFormatter(logging.Formatter):
    """Formatter personalizado com cores para o terminal"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


# Configurar logging
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter("%(levelname)s - %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
log = logging.getLogger(__name__)


def print_banner():
    """Exibe banner do CLI"""
    banner = """
    ╔══════════════════════════════════════════════╗
    ║     🚀 Airflow Docker CLI Manager 🐳        ║
    ║     Manage your Airflow environment easily   ║
    ╚══════════════════════════════════════════════╝
    """
    print(banner)


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="🛠️  Airflow Docker Helper CLI - Manage Airflow environments with ease",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  actl up              Start the Airflow environment
  actl status          Check environment status
  actl logs scheduler  View scheduler logs
  actl run my_dag      Run a specific DAG
  actl list            List all available DAGs
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Comando UP
    up_parser = subparsers.add_parser(
        "up", help="🚀 Start Docker environment", description="Start all Airflow services using Docker Compose"
    )
    up_parser.add_argument("--build", action="store_true", help="Rebuild images before starting")

    # Comando DOWN
    down_parser = subparsers.add_parser(
        "down", help="🛑 Stop Docker environment", description="Stop all Airflow services"
    )
    down_parser.add_argument("--volumes", action="store_true", help="Remove volumes (⚠️  deletes all data)")

    # Comando STATUS
    subparsers.add_parser(
        "status", help="📊 Check environment status", description="Display status of all Airflow containers"
    )

    # Comando LOGS
    logs_parser = subparsers.add_parser(
        "logs", help="📋 View container logs", description="View logs from Airflow containers"
    )
    logs_parser.add_argument(
        "service",
        nargs="?",
        choices=["webserver", "scheduler", "worker", "triggerer", "all"],
        default="all",
        help="Service to view logs from",
    )
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow log output")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of lines to show (default: 50)")

    # Comando RUN
    run_parser = subparsers.add_parser(
        "run", help="▶️  Run Airflow DAG", description="Execute a DAG inside the Docker container"
    )
    run_parser.add_argument("dag_id", nargs="?", help="DAG ID to run (optional if using config.yml)")
    run_parser.add_argument("--date", help="Execution date (YYYY-MM-DD)")

    # Comando LIST
    subparsers.add_parser(
        "list", help="📝 List available DAGs", description="Show all DAGs found in the dags directory"
    )

    # Comando FIX
    fix_parser = subparsers.add_parser(
        "fix", help="🔧 Run code linter", description="Check Python code quality with flake8"
    )
    fix_parser.add_argument("--autofix", action="store_true", help="Attempt to automatically fix issues (experimental)")

    # Comando SHELL
    shell_parser = subparsers.add_parser(
        "shell", help="💻 Open interactive shell", description="Open a bash shell in the Airflow worker container"
    )
    shell_parser.add_argument(
        "--service", default="worker", choices=["worker", "scheduler", "webserver"], help="Service to open shell in"
    )

    # Comando RESTART
    restart_parser = subparsers.add_parser(
        "restart", help="🔄 Restart services", description="Restart specific or all Airflow services"
    )
    restart_parser.add_argument("service", nargs="?", default="all", help="Service to restart (default: all)")

    args = parser.parse_args()

    # Se nenhum comando foi fornecido, mostra ajuda
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Verifica Docker (exceto para comando 'help')
    if args.command and args.command != "help":
        if not check_docker():
            log.error("❌ Docker is not ready. Please ensure Docker is installed and running.")
            sys.exit(1)

    # Executa o comando apropriado
    try:
        if args.command == "up":
            docker_up(build=args.build)
        elif args.command == "down":
            docker_down(volumes=args.volumes)
        elif args.command == "status":
            docker_status()
        elif args.command == "logs":
            docker_logs(args.service, follow=args.follow, lines=args.lines)
        elif args.command == "run":
            run_dag(dag_id=args.dag_id, execution_date=getattr(args, "date", None))
        elif args.command == "list":
            list_dags()
        elif args.command == "fix":
            fix_python_code(autofix=args.autofix)
        elif args.command == "shell":
            from .docker_utils import open_shell

            open_shell(args.service)
        elif args.command == "restart":
            from .docker_utils import restart_service

            restart_service(args.service)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        log.warning("\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        log.error(f"❌ Unexpected error: {e}")
        log.debug("Full traceback:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
