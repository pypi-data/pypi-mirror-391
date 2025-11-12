import sys
import os
import time as _t
import click
import questionary
from datetime import timedelta
from rich.console import Console
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from hpctools.makegen import generate_makefile
from hpctools.slurmgen import generate_slurm
from hpctools.utils import load_template, detect_modules, write_file
from hpctools.header import print_header
from questionary import path as qpath

console = Console()


def clear_console():
    """Cross-platform console clear."""
    os.system("cls" if os.name == "nt" else "clear")


def prompt_back_menu():
    """Reusable small pre-menu for quick back or exit."""
    action = questionary.select(
        "What do you want to do?",
        choices=[
            "Start configuration",
            "Go back to main menu",
            "Exit",
        ],
    ).ask()
    if action.startswith("Go back to main menu"):
        return "back"
    elif action.startswith("Exit"):
        sys.exit(0)
    return "start"


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """hpctools - HPC automation toolkit (Makefile + SLURM + Benchmarking)"""
    ctx.obj = {"deucalion_mode": False}

    while True:
        clear_console()
        print_header()

        mode_flag = "🌌 [Deucalion Mode: ON]" if ctx.obj["deucalion_mode"] else " [Standard Mode]"
        console.print(f"\n[bold cyan]{mode_flag}[/bold cyan]\n")

        choice = questionary.select(
            "Select an option:",
            choices=[
                "Generate Makefile",
                "Generate SLURM job script",
                "Generate both (Makefile + SLURM)",
                "View available templates",
                "Toggle Deucalion Mode",
                "Exit",
            ],
        ).ask()

        if choice.startswith("Generate Makefile"):
            clear_console()
            ctx.invoke(make)
        elif choice.startswith("Generate SLURM job script"):
            clear_console()
            ctx.invoke(slurm, deucalion_mode=ctx.obj["deucalion_mode"])
        elif choice.startswith("Generate both"):
            clear_console()
            ctx.invoke(all, deucalion_mode=ctx.obj["deucalion_mode"])
        elif choice.startswith("View available templates"):
            clear_console()
            ctx.invoke(templates)
        elif choice.startswith("Toggle Deucalion Mode"):
            ctx.obj["deucalion_mode"] = not ctx.obj["deucalion_mode"]
            clear_console()
            state = "enabled " if ctx.obj["deucalion_mode"] else "disabled "
            console.print(f"\n[green] Deucalion mode {state}.[/green]\n")
            _t.sleep(0.8)
        else:
            console.print("\n[bold cyan] Exiting HPC Tools. Goodbye![/bold cyan]\n")
            sys.exit(0)


# ------------------- MAKE -------------------
@cli.command()
@click.option("--template", is_flag=True, help="Use a Makefile template instead of manual input.")
def make(template):
    """Create a Makefile (interactive or template-based)."""
    clear_console()
    console.print("\n[bold cyan]🛠  Makefile Configuration[/bold cyan]\n")

    choice = prompt_back_menu()
    if choice == "back":
        return

    #Auto-detect available compiler modules
    modules = detect_modules()
    if modules:
        console.print("[bold cyan] Detected Environment Modules:[/bold cyan]")
        for name, versions in modules.items():
            versions_str = ", ".join(versions) if versions else "no versions listed"
            console.print(f"  [green]{name}[/green] → {versions_str}")
        console.print("[dim]Tip: You can load one of these before compiling if needed.[/dim]\n")
    else:
        console.print("[yellow] No module system detected or empty module list.[/yellow]\n")

    if not template:
        template = questionary.confirm("Generate from template?").ask()

    if template:
        tpl = qpath("Select Makefile template file:").ask() or "make_default.mk"
        tpl = os.path.expanduser(tpl.strip())
        compiler = questionary.text("Compiler (e.g. gcc, scorep gcc, clang) [gcc]:").ask() or "gcc"
        flags = questionary.text("Compilation flags [-O3 -Wall]:").ask() or "-O3 -Wall"
        ldflags = questionary.text("Linker flags (e.g. -lm -pthread) [-lm]:").ask() or "-lm"
        src = questionary.text("Source files (space-separated) [main.c]:").ask() or "main.c"
        output = questionary.text("Output executable [a.out]:").ask() or "a.out"
        generate_makefile(
            compiler, flags, ldflags, src, output,
            use_template=True, template_name=tpl
        )
    else:
        compiler = questionary.text("Compiler (e.g. scorep gcc, clang) [scorep gcc]:").ask() or "scorep gcc"
        flags = questionary.text("Compilation flags [-O3 -g -std=c99 -pedantic -Wall]:").ask() or "-O3 -g -std=c99 -pedantic -Wall"
        ldflags = questionary.text("Linker flags [-lm]:").ask() or "-lm"
        src = questionary.text("Source files (.c) [main.c]:").ask() or "main.c"
        output = questionary.text("Output executable [a.out]:").ask() or "a.out"
        generate_makefile(compiler, flags, ldflags, src, output)

    console.print("[green] Makefile successfully created![/green]")
    _t.sleep(1)

# ------------------- SLURM -------------------
@cli.command()
@click.option("--template", is_flag=True, help="Use a SLURM template instead of manual input.")
@click.option("--deucalion-mode", is_flag=True, help="Activate Deucalion cluster defaults.")
def slurm(template, deucalion_mode):
    """Create a SLURM job script (interactive or template-based)."""
    clear_console()
    console.print("\n[bold cyan] SLURM Job Configuration[/bold cyan]\n")

    choice = prompt_back_menu()
    if choice == "back":
        return

    # --- Account handling ---
    if deucalion_mode:
        console.print("[bold cyan] Deucalion mode enabled — preloading cluster defaults.[/bold cyan]")
        default_account = "f202500010hpcvlabuminhoa"
        account_prompt = f"SLURM account [{default_account}]:"
        account_default = default_account
    else:
        account_prompt = "SLURM account (leave blank if not applicable):"
        account_default = ""

    account = questionary.text(account_prompt, default=account_default).ask()
    if not deucalion_mode and account.strip() == "":
        account = ""

    # --- Basic SLURM config ---
    partition = questionary.text("Partition [normal-arm]:", default="normal-arm").ask() or "normal-arm"
    time = questionary.text("Time limit (hh:mm:ss) [00:35:00]:", default="00:35:00").ask() or "00:35:00"
    nodes = questionary.text("Number of nodes [1]:", default="1").ask() or "1"
    ntasks = questionary.text("Tasks per job [1]:", default="1").ask() or "1"
    cpus = questionary.text("CPUs per task [48]:", default="48").ask() or "48"
    exe = qpath("Executable path [./zpic]:").ask() or "./zpic"
    exe = os.path.expanduser(exe.strip())
    runs = questionary.text("Number of runs [5]:", default="5").ask() or "5"

    # --- Optional profiling / threading flags ---
    enable_scorep = questionary.confirm("Enable Score-P profiling?", default=False).ask()
    enable_perf = questionary.confirm("Enable perf statistics?", default=False).ask()
    enable_openmp = questionary.confirm("Use OpenMP threading (multi-thread runs)?", default=False).ask()

    # --- ETA estimation ---
    avg_time = questionary.text("Average time per run (seconds) [300]:", default="300").ask() or "300"
    try:
        total_runs = int(runs)
        avg_time_sec = int(avg_time)
    except ValueError:
        total_runs, avg_time_sec = 1, 300

    total_eta = timedelta(seconds=total_runs * avg_time_sec)
    console.print(f"\n[dim] Estimated total runtime: ~{total_eta}[/dim]\n")

    # --- Verify vs SLURM time limit ---
    def parse_slurm_time(slurm_time: str) -> int:
        parts = [int(p) for p in slurm_time.split(":")]
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = 0, parts[0], parts[1]
        else:
            h, m, s = parts[0], 0, 0
        return h * 3600 + m * 60 + s

    try:
        limit_seconds = parse_slurm_time(time)
        if total_runs * avg_time_sec > limit_seconds:
            console.print(
                f"[bold yellow] Warning:[/bold yellow] Estimated runtime ({total_eta}) "
                f"exceeds SLURM time limit ({time}). Consider increasing job time.\n"
            )
    except Exception:
        console.print("[dim]Unable to parse SLURM time for comparison.[/dim]")

    # --- Progress spinner ---
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]Preparing SLURM job script...[/cyan]"),
        transient=True,
    ) as progress:
        task = progress.add_task("wait", total=None)
        _t.sleep(1)

    # --- Generate SLURM content dynamically ---
    modules = []
    if enable_scorep:
        modules.append("module load Score-P/8.0")
    if enable_perf or "gcc" in exe:
        modules.append("module load GCC/13.3.0")

    module_lines = "\n".join(modules) if modules else "module purge"
    threads_line = 'THREADS="1 2 4 8"' if enable_openmp else 'THREADS="1"'
    omp_line = 'export OMP_NUM_THREADS=$nt' if enable_openmp else '# export OMP_NUM_THREADS=1'

    if enable_scorep:
        run_line = (
            f'SCOREP_EXPERIMENT_DIRECTORY="${{RUN_DIR}}/scorep" \\\n'
            f'    $EXEC > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/scorep.log"'
        )
    elif enable_perf:
        run_line = (
            f'perf stat -r 1 -e cycles,instructions,task-clock \\\n'
            f'    $EXEC > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/perf.log"'
        )
    else:
        run_line = f'$EXEC > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/error.log"'

    slurm_content = f"""#!/bin/bash
#SBATCH -A {account or ""}
#SBATCH -p {partition}
#SBATCH -t {time}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus}
#SBATCH --output=run_out.o%j
#SBATCH --error=run_err.e%j

{module_lines}

DATE=$(date +"%Y-%m-%d_%H-%M")
EXEC={exe}
{threads_line}
RUNS={runs}

mkdir -p results

for nt in $THREADS; do
    {omp_line}
    echo "Running with $nt thread(s)"
    for run in $(seq 1 $RUNS); do
        RUN_DIR="results/${{DATE}}_${{nt}}t_run${{run}}"
        mkdir -p "$RUN_DIR"
        {run_line}
    done
done
"""

    console.print(Syntax(slurm_content, "bash", theme="monokai", line_numbers=True))
    path = questionary.path("Save SLURM script to (default: ./run_job.sh):").ask() or "run_job.sh"
    if not os.path.splitext(path)[1]:
        path += ".sh"

    confirm = questionary.confirm("Do you want to save this script?", default=True).ask()
    if not confirm:
        console.print("[dim]Operation cancelled. Returning to menu.[/dim]")
        return

    write_file(path, slurm_content)
    console.print(f"[green] SLURM job script saved as {path}![/green]")
    _t.sleep(1)


# ------------------- ALL -------------------
@cli.command()
@click.option("--deucalion-mode", is_flag=True, help="Activate Deucalion cluster defaults.")
@click.pass_context
def all(ctx, deucalion_mode):
    """Generate both Makefile and SLURM job script."""
    clear_console()
    ctx.invoke(make)
    ctx.invoke(slurm, deucalion_mode=deucalion_mode)


# ------------------- TEMPLATES -------------------
@cli.command()
def templates():
    """List, preview, or apply available templates."""
    clear_console()

    base_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(base_dir):
        console.print("[red] No templates directory found.[/red]")
        return

    files = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
    if not files:
        console.print("[yellow] No template files found in hpctools/templates/[/yellow]")
        return

    console.print("\n[bold cyan] Available Templates:[/bold cyan]\n")
    for i, f in enumerate(files, 1):
        console.print(f"  {i}) [green]{f}[/green]")

    choice = questionary.text("\nEnter the template number to open (or press Enter to exit): ").ask()
    if not choice or not choice.isdigit() or int(choice) < 1 or int(choice) > len(files):
        console.print("\n[dim]Exiting template viewer.[/dim]")
        return

    template_file = files[int(choice) - 1]
    full_path = os.path.join(base_dir, template_file)

    try:
        content = load_template(template_file)
        syntax = Syntax(content,
                        "make" if template_file.endswith(".mk") else "bash",
                        theme="monokai", line_numbers=True)

        console.print(f"\n[bold blue]🔍 Template selected:[/bold blue] {template_file}\n")

        action = questionary.select(
            "Choose an action:",
            choices=[
                "Preview",
                "Apply → Generate in current folder",
                "Cancel",
            ],
        ).ask()

        if action.startswith("Preview"):
            console.print(syntax)
            console.print("\n[dim]You can re-run this command to apply the template later.[/dim]")
            return

        elif action.startswith("Apply"):
            clear_console()
            console.print(f"[bold cyan] Applying template:[/bold cyan] {template_file}")
            
    except Exception as e:
        console.print(f"[red] Failed to load template:[/red] {e}")
        return
