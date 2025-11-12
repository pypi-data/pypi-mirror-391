from hpctools.utils import load_template, write_file, success, error, timestamp

def generate_slurm(
    account, partition, time, nodes, ntasks, cpus, exe, runs,
    use_template: bool = False,
    template_name: str = "slurm_default.sh",
    enable_scorep: bool = False,
    enable_perf: bool = False,
    enable_openmp: bool = False,
) -> bool:
    """Generate a SLURM job script, with optional Score-P / perf / OpenMP integration."""

    try:
        # --- Template case ---
        if use_template:
            template = load_template(template_name)
            slurm = template.format(
                account=account,
                partition=partition,
                time=time,
                nodes=nodes,
                ntasks=ntasks,
                cpus=cpus,
                exe=exe,
                runs=runs,
                date=timestamp(),
            )

        # --- Dynamic fallback (no template) ---
        else:
            modules = []
            if enable_scorep:
                modules.append("module load Score-P/8.0")
            if "gcc" in exe or enable_perf:
                modules.append("module load GCC/13.3.0")

            module_lines = "\n".join(modules) if modules else "module purge"

            threads_line = 'THREADS="1"' if not enable_openmp else 'THREADS="1 2 4 8"'
            omp_line = 'export OMP_NUM_THREADS=$nt' if enable_openmp else '# export OMP_NUM_THREADS=1'

            # Conditional profiling command
            if enable_scorep:
                run_line = (
                    f'SCOREP_EXPERIMENT_DIRECTORY="${{RUN_DIR}}/scorep" \\\n'
                    f'    {exe} > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/scorep.log"'
                )
            elif enable_perf:
                run_line = (
                    f'perf stat -r 1 -e cycles,instructions,task-clock \\\n'
                    f'    {exe} > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/perf.log"'
                )
            else:
                run_line = f'{exe} > "${{RUN_DIR}}/output.log" 2> "${{RUN_DIR}}/error.log"'

            slurm = f"""#!/bin/bash
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

        # --- Save to disk safely ---
        write_file("run_job.slurm", slurm)
        success("SLURM script successfully generated.")
        return True

    except Exception as e:
        error(f"Failed to create SLURM script: {e}")
        return False
