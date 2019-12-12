import argparse
import subprocess
import re
import os
import time

job_id_regex = r"(\d+)(?:_\[\d+\-\d+\])?"


def get_job_id(job_line):
    # Extract the correct job id from both possible job id
    # line formats of squeue output (123456 or 123456_[1-2])
    match = re.match(job_id_regex, job_line)

    return int(match.group(1))


def delete_jobs(first_id, last_id):
    # Deletes all jobs (array or single) of the user that are in the range [first_id, last_id]

    # This section reads all current jobs of the user
    user = os.environ['USER']
    current_jobs = subprocess.Popen(
        ['squeue', f'--user={user}', '--noheader', '--format=%i'], stdout=subprocess.PIPE).stdout
    current_jobs = [line.rstrip().decode('utf-8')
                    for line in current_jobs.readlines()]

    # We delete all user jobs in the given range, spacing 'scancel' calls with a 1s delay
    for job_line in current_jobs:
        job_id = get_job_id(job_line)

        if job_id >= first_id:
            if job_id <= last_id:
                print(f'Cancelling job {job_id}')
                subprocess.run(['scancel', str(job_id)])
                time.sleep(1)
            else:
                break


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('first_job_id', type=int,
                        help='ID of the first job to be cancelled.')
    parser.add_argument('last_job_id', type=int,
                        help='ID of the last job to be cancelled. This ID will be included in the cancelled jobs.')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    delete_jobs(args.first_job_id, args.last_job_id)
