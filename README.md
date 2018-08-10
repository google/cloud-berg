# Cloud Berg

### Design goal
Berg is a minimal tool for running experiments with GPU instances on Cloud and storing the results in a bucket. It’s 400 lines of python.
 
### Non-goals

- not designed to run on anything beside google cloud
- not designed to host a production web server
- not designed to do anything clever


## Installation

Clone and install the berg tool on your local machine
After installing gcloud, run the following locally 

```bash
gcloud init
gcloud auth login # Use your @google account
gcloud source repos clone berg --project=cloud-berg
pip install -e berg
berg init # Set up your configuration correctly in ~/.berg/berg.json
```



## Basic usage

Launch two experiments (that each use all the GPUs on single instance, and shut down after they complete their job)
```bash
cd <your_git_repo>
berg run "python train.py --bs=256 --logdir=/root/berg_results/sweep1/bs_256" 
```

The python command will be run from the root of your github repo. It will run rsync files from `/root/berg_results/sweep1/` and results will show up in  `gs://<your_berg_bucket>/berg_results/sweep1`

### Launch a devbox with 4 p100 gpus, CUDA, Tensorflow and Pytorch
```bash
berg devbox
```
After it starts you can ssh into it with `berg ssh <instance_name>`


## How does berg work?

The best way to understand berg is to just read the code (it's very small). Here’s an even shorter TLDR:

Executing berg run <cmd> does the following:

- Copy the local git repo that you’re working on to GCS 
- Generate a job-specific <job_name>_metadata.json file with the cmd and the current  git_commit and copy it to GCS
- Start an instance to process that job (using the config info in ~/.berg/berg.json)

Once the instance starts, it executes berg-worker run which does the following:

- Copy down  <job_name>_metadata.json from GCS and parse the file
- Copy down the git repo from GCS, check out your commit and install any requirements in setup.py
- Start regularly uploading logs from /root/berg_results/<results_dir>
- Run the cmd for the job
- Shut down the instance after the job finishes


## Managing berg jobs

Helpful shortcuts (all of which are aliases for gcloud commands)
```bash
berg list # list all running instances 
berg tail <inst_name> # tail logs
berg log <inst_name> # get all logs
berg ssh <inst_name> # ssh into an instance (then run `tt` to get tmux panes)
berg kill <inst_name> # kill an experiment
berg sync <inst_name> # sync local code to a running instance (for development)
```

You can also use the gce web interface which allows filtering and bulk management of all of your instances.

## Running a large scale job with MPI

```bash
berg devbox -m <num_machines>
```
This will start `num_machines` devboxes with 4 GPUs each. 

Then ssh into the first machine, and run `mpi <your program>` to run your program across all machines using MPI. Here mpi is an alias calling mpirun with all the necessary flags, and starting one worker process per GPU in your cluster. The easiest way of running multi machine tensorflow/pytorch experiments is to use Horovod, which now comes pre-installed on the golden image.


## Creating a custom golden image
If you’d like to use a different image, you can edit the default_image value in `~/.berg/berg.json`

We recommend starting with one of the [official GCE deep learning images](https://blog.kovalevskyi.com/deep-learning-images-for-google-cloud-engine-the-definitive-guide-bc74f5fb02bc), and then modifying it slightly.

Berg will log into your image as the `root` user, and requires the following:

- python installed with conda in  /root/anaconda3/bin
- A directory of code repositories in /root/code
- Berg cloned to /root/code/berg and installed with pip install -e ~/code/berg