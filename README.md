# Compute Canada Guidelines

Compute Canada (CC) provides access to numerous supercomputing resources, allowing to reach next-level compute power for research projects. This repository aims to provide an easy-to-use guide on how to upscale a research project from local to Compute Canada computing.
A French video presentation of most of the content listed here is [available on Youtube](https://www.youtube.com/watch?v=koyBeOLtRDk). 

## Contents

This repository stores a summarized version of the very complete [Compute Canada Documentation](https://docs.computecanada.ca/wiki/Compute_Canada_Documentation) as well as some potentially useful files when using CC. Most of the stored files are generic and therefore require basic modifications to be used inside a research project.

## Prerequisites

Before being allowed to connect a Compute Canada, one must obtain a CC account. The procedure is fast and only requires knowledge of an associated professor's CCRI number. The complete account creation procedure can be found [here](https://www.computecanada.ca/research-portal/account-management/apply-for-an-account/).

## Basic usage

### Connection to a cluster

Compute Canada offers a [multitude of clusters](https://docs.computecanada.ca/wiki/Getting_started#What_resources_are_available.3F), each with its specific dedicated resources. In order to connect to a specific cluster, open a terminal and enter the following command :

```
$ ssh userid@cluster_name.computecanada.ca
```

where `userid` is replaced with your account's id (i.e. _magod_) and `cluster_name` is the target cluster name (i.e. _beluga_). You will then be prompted to enter you password, which is the one you used when you created your CC account. Once connected, you will arrive in your personal Compute Canada directory.

### Connection to a single computing node

When connecting to a cluster, you are automatically located in a _login_ node. These nodes do not have access to any interesting compute power and should therefore never be used for script execution. Instead, clusters own a varying amount of _computing_ nodes, specifically designed to execute scripts.

It is possible to interactively connect to computing node(s) via the following command :

```
$ salloc --time=1:0:0 --ntasks=N --account=def-someuser
```

The above line requests allocation of `N` tasks (corresponding to CPU cores), for a time of one hour, on behalf of the account `def-someuser`. Note that the account name to be used can be found via the procedure found [here](https://docs.computecanada.ca/wiki/Running_jobs#Accounts_and_projects).

When logged on a compute node, you have sole access to the resources you requested. Note that your _address_ (prefix to your bash commands) also changed, it should now look like [userid@blg4117 ~] instead of [userid@beluga1 ~]. You can also see all of the (shared) compute node's resources via the `htop` command. **N.B. The above procedure is only shown to provide insight on the login and compute nodes differences. You should use the following procedure to launch jobs.**

### Running jobs

The recommended procedure to launch jobs on a Compute Canada supercomputer is to use the [Slurm](https://slurm.schedmd.com/) job scheduler. All jobs must be contained inside a simple bash file (which can simply launch a Python script for example). Given such a bash file named `simple_script.sh`,

```
#!/bin/bash
#SBATCH --time=00:15:00
#SBATCH --account=def-someuser
echo 'Hello, world!'
sleep 30
```

we submit a job to the cluster via the following command :

```
$ sbatch simple_script.sh
```

The above command will ask the job scheduler for allocation of the resources required by the bash script (see the next [section](#Hyperparams) for more details). Once the needed resources are allowed, a compute node is assigned to the job and execution of the script is launched.

Note that the default location of your script's output will be in a "slurm-{JOB_ID}.out" file, located in the directory where the job was launched.

### Basic hyperparameter configuration

As can be seen in the above `simple_script.sh`, some _SBATCH_ arguments may be contained into the bash file, effectively specifying what are the required resources for the launched job. The mandatory _SBATCH_ arguments are _time_ and _account_, but you will probably wish to specify more of them, like the number of cpus (_--cpus-per-task_), the required RAM (_--mem_) or the number of GPUs (_--gres=gpu:N_). An example of a more plausible launch script with more arguments is the given `generic_launcher.sh`, which incorporates many concepts that will be explained further below. A complete list of all available arguments can also be found [here](https://slurm.schedmd.com/sbatch.html).

**It is important to note here that any job that exceeds its requested resources (whether it takes too long or requires too much memory) will be automatically stopped by the job scheduler and marked as failed** (more info [here](#Email)). Since the more resources we request for a job, the longer it will take for the job to be launched (see [here](https://docs.computecanada.ca/wiki/What_is_a_scheduler%3F) for more details on how a scheduler works), we will wish to request just enough resources for our job to be sure to complete while ensuring it still launches as quickly as possible. The next [section](#Finding-the-good-amount-of-resources-to-request) aims to provide a simple procedure to help determine the correct amount of resources to request.

### Finding the good amount of resources to request

In order to find just the right amount of resources to request, one should first find confident upper bounds on both its job's time and memory requirements. Say you expect your normal job time to be of 2 hours, when running on 6 CPUs and your memory requirement to never exceed 100G. You should now launch your job with a bash file requesting even larger resources, let's say 3 hours and 125G.

Upon completion of the job, you can now inspect its efficiency with the `seff {JOB_ID}` command, which could yield:

```
$ seff 12345678
Job ID: 12345678
Cluster: graham
User/Group: jsmith/jsmith
State: COMPLETED (exit code 0)
Cores: 6
CPU Utilized: 02:48:58
CPU Efficiency: 99.72% of 02:49:26 core-walltime
Job Wall-clock time: 02:49:26
Memory Utilized: 213.85 MB
Memory Efficiency: 0.17% of 125.00 GB
```

In this particular example, we first note that the amount of memory requested is way too high and we should therefore be more than safe enough by requesting 2G per job. Furthermore, the bottleneck on our computation time seems to be on the CPU utilization: we could therefore request more CPUs for the jobs to be completed quicker.

The chosen amount of resources should now be adapted to the supercomputer you are launching on. Specific details on a supercomputer's node charactesterics are available for all clusters (i.e. [here](https://docs.computecanada.ca/wiki/Graham#Node_characteristics) for Graham). The basic idea here is that you wish your job to be available to run on as many nodes as possible to enable faster launching. Therefore, it might be faster to launch a job requesting 32 CPUs for only one hour than one that requires 6 CPUs for 6 hours. See [here](https://docs.computecanada.ca/wiki/Job_scheduling_policies) for more details on how the jobs are assigned and on optimization of your job launching priority.

## Managing the runs

### Monitoring current jobs

Once runs are launched, it is possible to monitor them via the `squeue` (or `sq`) command. To view your personal jobs, simply enter the command `squeue -u $USER` or `sq` and you will have access to an output like this :

```
   JOBID     USER      ACCOUNT      NAME  ST   TIME_LEFT NODES CPUS    GRES MIN_MEM NODELIST (REASON)
  123456   smithj   def-smithj  simple_j   R        0:03     1    1  (null)      4G cdr234  (None)
  123457   smithj   def-smithj  bigger_j  PD  2-00:00:00     1   16  (null)     16G (Priority)
```

where you will see every job you submitted to the job scheduler that has not yet terminated. A `R` status indicates the job is running, while a `PD` status indicates it is pending (i.e. awaiting for its requires resources).

### Cancelling jobs

Use `scancel` with the job ID to cancel a job:

```
$ scancel <jobid>
```

You can also use it to cancel all your jobs, or all your pending jobs:

```
$ scancel -u $USER
$ scancel -t PENDING -u $USER
```

### Launching multiple jobs

The true use case of a supercomputer is to launch a large number of jobs. While launching ourselves every single run by typing the `sbatch` call can be viable for a few runs, it is absolutely essential to be able to programmatically launch runs when their number is considerable.

To do so, it is absolutely possible to use a custom Python script launching the `sbatch` commands. An example of such a script can be found in the `launcher.py` file. Note that this runner incorporates some concepts that are introduced in the following sections, including overloading the default _SBATCH_ arguments in the bash file and passing arguments to your job script. Note that the provided file separates calls to `sbatch` by 1 second, as per CC's recommendations.

### Cancelling multiple jobs

If we just launched a large number of jobs and wish to cancel them (i.e. because the first one of them failed due to a typo), we might wish to cancel all jobs inside a given range of jobs. The `cancel_jobs.py` provides exactly this functionality, with the following call format:

```
$ python cancel_jobs.py 4658822 4658928
Cancelling job 4658822
Cancelling job 4658924
Cancelling job 4658928
```

In the above example, all user owned jobs with IDs in the range [4658822, 4658928] are cancelled while other jobs are left untouched.

## File System

Unlike your personal computer, a Compute Canada system will typically have several storage spaces or filesystems and you should ensure that you are using the right space for the right task. In this section we will discuss the principal filesystems available on most Compute Canada systems and the intended use of each one along with some of its characteristics.

- **HOME**: While your home directory may seem like the logical place to store all your files and do all your work, in general this isn't the case - your home normally has a relatively small quota and doesn't have especially good performance for the writing and reading of large amounts of data. The most logical use of your home directory is typically source code, small parameter files and job submission scripts.

- **PROJECT**: The project space has a significantly larger quota and is well-adapted to [sharing data](https://docs.computecanada.ca/wiki/Sharing_data) among members of a research group since it, unlike the home or scratch, is linked to a professor's account rather than an individual user.

- **SCRATCH**: For intensive read/write operations, scratch is the best choice. Remember however that important files must be copied off scratch since they are not backed up there, and older files are subject to [purging](https://docs.computecanada.ca/wiki/Scratch_purging_policy). The scratch storage should therefore only be used for transient files.

All users can check the available disk space and the current disk utilization for the _project_, _home_ and _scratch_ file systems with the command line utility `diskusage_report`, available on Compute Canada clusters. Following is a typical output of this utility:

```
$ diskusage_report
                             Description                Space           # of files
                        /home (username)              14G/50G            211k/500k
                     /scratch (username)            5906M/20T           170k/1000k
               /project (group username)              0/2048k               0/2048
           /project (group def-someuser)            15G/1000G             524/500k
          /nearline (group def-someuser)            15G/1000G             524/500k

```

The above output shows your different available file storage systems, as well as their usage percentages in both space and number of files.

## Python recommendations

Using Python on Compute Canada clusters is a bit different than on your local computer. Due to the configuration of the clusters, CC suggests to create Python virtual environments inside each job on the compute node. To do so, one must first create a _requirements.txt_ file, containing a given job's dependencies. On a machine containing all the required libraries, one can simply enter

```
pip freeze > requirements.txt
```

to generate a complete requirements.txt file for a given project. Once this file is generated, we need to do some manipulations in order to create a Python virtual environment, activate it and then install the needed requirements inside our launching script. These manipulations are :

```
module load python/3.7
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt
```

where version 3.7 of Python is used. These lines are included in both generic launcher bash files.

The major difference to note here is the use of the `--no-index` option. This option tells pip to install packages via the Compute Canada wheelhouse instead of the Internet, since Internet is not available on compute nodes. Note that the above instructions require all of the packages you need to be available in the python wheels that Compute Canada provides. If you think that the missing wheel should be included in the Compute Canada wheelhouse, please contact their [Technical support](https://docs.computecanada.ca/wiki/Technical_support) to make a request.

## Advanced hyperparameter configuration

While the above procedure will allow for most use cases to be handled, some more advanced usages of the Compute Canada clusters may require some more functionalities.

### Running a job array

When doing research, we will often find ourselves in the situation where we wish to run a single job with the same configuration a multitude of times, i.e. to attest of our method's stability by changing the random seed. In those cases, Compute Canada recommends to use array jobs.

Also known as a task array, an array job is a way to submit a whole set of jobs with one command. The individual jobs in the array are distinguished by an environment variable, `$SLURM_ARRAY_TASK_ID`, which is set to a different value for each instance of the job. The `generic_array_launcher.sh` contains an example which launches 10 instances of a single job. See [here](https://docs.computecanada.ca/wiki/Job_arrays) for a more in-depth guide on how to use job arrays.

### Overloading via sbatch call

In some cases, a generic bash launcher file cannot be used for all the jobs we wish to run because they have different resource requirements. For those cases, it is useful to know that is is also possible to specify directives as command-line arguments to `sbatch`. For example,

```
$ sbatch --time=00:30:00 simple_script.sh
```

will override the time limit set in the `simple_script.sh` file to force a time limit of 30 minutes.

This _SBATCH_ arguments overriding is already included in the provided `launcher.py` script, showing you an example on how your launcher could distinguish between resource allocation arguments and job arguments.

### Email

You can ask to be notified by email of certain job conditions by supplying options to `sbatch`.

```
#SBATCH --mail-user=<email_address>
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL
```

The provided launch bash files send emails for each failed job.

### Output redirection

Another interesting _SBATCH_ argument to consider is the `--output`. This argument tells SLURM where you wish the output of your job to be written. When unspecified, the output is placed in a file named "slurm-", suffixed with the job ID number and ".out", i.e. `slurm-123456.out`, in the directory from which the job was submitted.

The provided launch bash files automatically write the output files in the scratch directory, with filenames corresponding to the job type: "jobID_arrayID.out" for array jobs and "jobID.out" for single jobs.

Note that, if you wish the output to be written in a different directory than the one from which the job was submitted, you must specify the complete absolute filepath and ensure that all subdirectories exist before launching the jobs.

## Varia

### Python print particuliarities

When a job is running, one might wish to see its status by printing various updates via the `print()` Python function. Simply using the print function on a supercomputer might not yield the desired outcome, as the console output is only flushed once the job is finished. Three main options are available to tackle this problem:

- **Launching Python in unbuffered mode**: Using the `-u` option in your python launching line `python -u my_script.py` forces the stdout and stderr streams to be unbuffered, resulting in `print()` calls being immediately processed.

- **Using the logging library**: You could replace the print calls with corresponding calls in the `logging` [library](https://docs.python.org/3/library/logging.html). All logging calls made through this library are automatically flushed and it also contains numerous quality-of-life improvements over the default print calls.

- **Adding the flush=True option**: You _could_ replace all of your print calls by adding the flush=True option, i.e. `print('Hello World', flush=True)`. This option is however time consuming and should never be the option of choice for any serious project.

- **Adding sys.stdout.flush() calls**: Instead of flushing on every print, you could also only flush at specific moments, by calling the `sys.stdout.flush()` function from the `std` library.

### Race conditions

For users new to supercomputers, it is quite important to remember that your jobs might run at the _exact_ same time, so [race conditions](https://en.wikipedia.org/wiki/Race_condition) might occur. Be especially cautious around all reading/writing of shared files, amongst other things.

## Contributing

This guideline aims to help as many as possible. If you wish to add something or maybe correct some sections of this guideline, feel free to open a [Pull Request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).
