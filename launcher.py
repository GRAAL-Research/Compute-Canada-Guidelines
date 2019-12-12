import os
import subprocess
import time


def args_formatter(args):
    # Utility function for command line arguments formatting
    return ['--{}={}'.format(name, value) for name, value in args.items()]


def launch_job(run_args, sbatch_args):
    # Dispatch function
    # Replace 'my_launcher.sh' with your own bash file
    # As per CC recommendations, all sbatch calls are separated by 1 second
    subprocess.Popen(['sbatch', *args_formatter(sbatch_args),
                      'my_launcher.sh', *args_formatter(run_args)])
    time.sleep(1)


def main():
    # This example would launch two separate jobs: one running on a GPU and another one on CPU.

    # Each run has a specific bool value for a 'cuda' arg as well as a different random seed
    run_args_list = [{'cuda': True, 'seed': 42},
                     {'cuda': False, 'seed': 13}]

    # For the GPU job, we override the requirements by requesting a GPU.
    # For the CPU job, we change the memory, time and CPU number requirements.
    sbatch_args_list = [{'gres': 'gpu:1'},
                        {'mem': '32G', 'time': '0-05:00', 'cpus-per-task': 32}]

    # We launch each job with its corresponding run and sbatch_args
    for run_args, sbatch_args in zip(run_args_list, sbatch_args_list):
        launch_job(run_args, sbatch_args)


if __name__ == '__main__':
    main()
