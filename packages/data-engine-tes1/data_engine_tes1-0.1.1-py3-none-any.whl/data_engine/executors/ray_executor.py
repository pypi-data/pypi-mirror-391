# tool/executors/ray_executor.py
import os
import re
import time
import json
import subprocess
import logging
import shlex
from typing import Optional
from data_engine.utils.env_utils import exit_with_error
from loguru import logger


def extract_jobid(master_addr: str) -> str:
    m = re.search(r"job-([0-9a-f-]+)(?=-master)", (master_addr or ""))
    return m.group(1) if m else "unknown"


def start_ray_head(jobid: str, world_size: int, port: int = 6379):
    try:
        dashboard_port = os.environ.get("RAY_DASHBOARD_PORT", "8265")
        subprocess.run(
            [
                "ray",
                "start",
                "--head",
                f"--port={port}",
                "--dashboard-host=0.0.0.0",
                f"--dashboard-port={dashboard_port}",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Failed to start Ray head: {e}")
    logger.info("Ray head started.")


def wait_for_ray_workers(world_size: int):
    logger.info("Waiting for worker nodes...")
    timeout_sec = int(os.environ.get("RAY_WAIT_TIMEOUT_SEC", "600"))
    start_ts = time.time()
    sleep_s = 1.0
    while True:
        try:
            info = subprocess.check_output(
                ["ray", "list", "nodes", "--format", "json"], text=True
            )
            nodes = json.loads(info)
            alive_nodes = [n for n in nodes if n.get("state") == "ALIVE"]
            logger.info(f"Ray alive: {len(alive_nodes)}/{world_size}")
            if len(alive_nodes) >= world_size:
                break
        except Exception as e:
            logger.warning(f"Checking Ray nodes failed: {e}")
        if time.time() - start_ts > timeout_sec:
            exit_with_error(f"Timed out waiting for Ray workers after {timeout_sec}s")
        time.sleep(min(sleep_s, 5.0))
        sleep_s *= 1.2
    logger.info("All Ray nodes ready.")


def submit_ray_job(
    config_path: str,
    root_dir: str,
    package_mode: bool = False,
    package_working_dir: Optional[str] = None,
    package_startup_cmd: Optional[list] = None,
):
    try:
        from ray.job_submission import JobSubmissionClient, JobStatus  # type: ignore
    except Exception as e:
        exit_with_error(f"Ray job submission client not available: {e}")

    endpoint = (
        os.environ.get("RAY_DASHBOARD_ADDRESS")
        or os.environ.get("RAY_JOB_SUBMISSION_ADDRESS")
        or "http://127.0.0.1:8265"
    )
    client = JobSubmissionClient(endpoint)

    if package_mode:
        if not package_working_dir or not package_startup_cmd:
            exit_with_error(
                "Internal: package mode requires package_working_dir and package_startup_cmd"
            )
        runtime_env = {"working_dir": package_working_dir}
        entrypoint = shlex.join(package_startup_cmd)
        logger.info(
            f"Submitting Ray job (package mode). entrypoint={entrypoint}, runtime_env working_dir will be uploaded."
        )
        try:
            job_id = client.submit_job(entrypoint=entrypoint, runtime_env=runtime_env)
        except Exception as e:
            exit_with_error(f"Failed to submit Ray package job: {e}")
    else:
        entry = f"python {shlex.quote(os.path.join(root_dir, 'tool', 'launcher.py'))} {shlex.quote(config_path)}"
        try:
            job_id = client.submit_job(entrypoint=entry)
        except Exception as e:
            exit_with_error(f"Failed to submit Ray job: {e}")

    logger.info(f"Job submitted. ID: {job_id}")
    seen_len = 0
    while True:
        try:
            info = client.get_job_info(job_id)
            status = info.status
            logs = client.get_job_logs(job_id) or ""
            if seen_len < len(logs):
                print(logs[seen_len:], end="")
                seen_len = len(logs)
            if status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}:
                logger.info(f"Job finished with status: {status}")
                if status != JobStatus.SUCCEEDED:
                    exit_with_error(f"Ray job did not succeed. Final status: {status}")
                break
        except Exception as e:
            # transient polling errors should not immediately abort
            logger.warning(f"Error polling job status/logs: {e}")
        time.sleep(5)


def join_ray_worker(master_addr: str):
    if not master_addr:
        exit_with_error("MASTER_ADDR must be set for ray worker join")
    ray_address = f"{master_addr}:6379"
    try:
        subprocess.run(
            ["ray", "start", "--block", "--address", ray_address], check=True
        )
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Failed to start Ray node: {e}")


def start_ray_and_submit(
    config_path: str,
    world_size: int,
    master_addr: str,
    root_dir: str,
    package_mode: bool = False,
    package_working_dir: Optional[str] = None,
    package_startup_cmd: Optional[list] = None,
):
    jobid = extract_jobid(master_addr)
    start_ray_head(jobid, world_size)
    wait_for_ray_workers(world_size)
    submit_ray_job(
        config_path=config_path,
        root_dir=root_dir,
        package_mode=package_mode,
        package_working_dir=package_working_dir,
        package_startup_cmd=package_startup_cmd,
    )
