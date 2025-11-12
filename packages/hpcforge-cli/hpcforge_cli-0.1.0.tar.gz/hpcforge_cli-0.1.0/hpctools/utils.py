import os
import subprocess
from datetime import datetime
from rich.console import Console
import subprocess
import shutil
from datetime import timedelta
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import platform

# Global rich console
console = Console()

# ======================================================
#   FILE I/O UTILITIES
# ======================================================

def write_file(path: str, content: str) -> None:
    """
    Write UTF-8 text content to a file, creating parent directories if necessary.
    Overwrites existing files safely.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        # Normalize newlines and ensure UTF-8 compatibility
        safe_content = content.strip().replace("\r\n", "\n") + "\n"

        # Always write as UTF-8 (fixes Windows charmap errors)
        with open(path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(safe_content)

        success(f" File written: {path}")
    except Exception as e:
        error(f" Failed to write file '{path}': {e}")

def ensure_dir_exists(path: str) -> None:
    """Ensure that a directory exists (create it if missing)."""
    os.makedirs(path, exist_ok=True)

def load_template(name: str) -> str:
    """
    Load a template from the internal templates/ directory.
    Raises FileNotFoundError if the file doesn't exist.
    """
    base_dir = os.path.join(os.path.dirname(__file__), "templates")
    full_path = os.path.join(base_dir, name)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Template not found: {full_path}")
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

# ======================================================
#   OUTPUT / LOGGING UTILITIES
# ======================================================

def success(msg: str) -> None:
    """Print a success message with a green checkmark."""
    console.print(f"[bold green]✅ {msg}[/bold green]")

def warn(msg: str) -> None:
    """Print a yellow warning message."""
    console.print(f"[bold yellow]⚠️  {msg}[/bold yellow]")

def error(msg: str) -> None:
    """Print a red error message."""
    console.print(f"[bold red]❌ {msg}[/bold red]")

# ======================================================
#   TIME UTILITIES
# ======================================================

def timestamp(fmt: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """Return the current timestamp formatted according to `fmt`."""
    return datetime.now().strftime(fmt)

# ======================================================
#   SHELL / SYSTEM UTILITIES
# ======================================================

def run_cmd(cmd: str, show_output: bool = True) -> int:
    """
    Execute a shell command and return its exit code.
    Captures stdout/stderr for better error handling.
    """
    console.print(f"[cyan]$ {cmd}[/cyan]")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        )
        if show_output and result.stdout.strip():
            console.print(result.stdout)
        return result.returncode
    except subprocess.CalledProcessError as e:
        error(f"Command failed with exit code {e.returncode}")
        if e.stderr:
            console.print(f"[red]{e.stderr.strip()}[/red]")
        return e.returncode
    except FileNotFoundError:
        error("Shell command not found. Ensure it exists in your PATH.")
        return 127
    
# ======================================================
#   MODULE DETECTION UTILITIES
# ======================================================
    
def detect_modules():
    """
    Detects available environment modules (GCC, Clang, Intel, Score-P, etc.)
    Returns a dictionary of module names -> list of versions.
    """
    if not shutil.which("module"):
        return {}

    try:
        result = subprocess.run(
            "module avail 2>&1 | grep -E 'GCC|Clang|Intel|Score|OpenMPI|CUDA'",
            shell=True, text=True, capture_output=True
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        modules = {}

        for line in lines:
            # Try to split module name and version
            parts = line.split("/")
            if len(parts) == 2:
                name, version = parts
                modules.setdefault(name, []).append(version)
            else:
                # e.g. "GCC" without version
                modules.setdefault(parts[0], [])

        return modules

    except Exception:
        return {}    
    
    
# ======================================================
#   RUNTIME ESTIMATION UTILITIES
# ======================================================
def estimate_runtime(runs: int, per_run_estimate: int = 300):
    """
    Estimate total runtime and display a spinner with ETA info.

    Args:
        runs (int): Number of runs.
        per_run_estimate (int): Estimated seconds per run (default = 300s = 5min).

    Example:
        estimate_runtime(8) → prints "Estimated runtime: ~00:40:00"
    """
    eta = timedelta(seconds=runs * per_run_estimate)
    print(f"\n[dim]Estimated runtime: ~{eta}[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Estimating runtime...[/cyan]"),
        transient=True,
    ) as progress:
        task = progress.add_task("waiting", total=None)
        # Simulate short delay for realism
        time.sleep(1)
        progress.update(task, description="[green]✅ Ready to run jobs![/green]")


# ======================================================
#   CMD CLEANUP SCREEN
# ======================================================

def clear_console() -> None:
    """Cross-platform console clear."""
    # On Windows, use cls; otherwise, clear
    command = "cls" if platform.system().lower().startswith("win") else "clear"
    os.system(command)