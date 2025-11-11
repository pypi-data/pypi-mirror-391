#!/usr/bin/env python3
import os, asyncio
import sys
import subprocess
import time
import json
import re
from typing import Tuple
import shutil
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from data_engine.utils.s3_utils import download_from_s3

nvidia_smi_path = "/usr/bin/nvidia-smi"

if os.path.isfile(nvidia_smi_path) and os.access(nvidia_smi_path, os.X_OK):
    try:
        try:
            output = (
                subprocess.check_output([nvidia_smi_path], stderr=subprocess.DEVNULL)
                .decode()
                .strip()
            )
        except Exception as e:
            output = None
        if not output:
            print("nvidia-smi 返回空，删除 /usr/bin/nvidia-smi")
            os.remove(nvidia_smi_path)
        else:
            print("nvidia-smi 正常，有输出")
    except subprocess.CalledProcessError:
        print("执行 nvidia-smi 失败")
else:
    print("/usr/bin/nvidia-smi 不存在或不可执行")


def exit_with_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def ensure_s3_conf() -> dict:
    conf = {}
    ak = os.environ.get("S3AK")
    sk = os.environ.get("S3SK")
    url = os.environ.get("S3URL")
    if ak and sk and url:
        verify_env = os.environ.get("S3VERIFY", "false").strip().lower()
        verify = verify_env in {"1", "true", "yes"}
        conf = {
            "aws_access_key_id": ak,
            "aws_secret_access_key": sk,
            "endpoint_url": url,
            "verify": verify,
        }
    return conf


def download(source: str, run_path: str):
    s3_conf = ensure_s3_conf()
    result_path = source
    if source.startswith("s3://"):
        if not s3_conf:
            exit_with_error(
                "S3 credentials are required for s3 config path (S3AK/S3SK/S3URL)"
            )
        try:
            loca_path = os.path.join(run_path, "download")
            result_path = download_from_s3(source, loca_path, s3_conf)
        except Exception as e:
            exit_with_error(f"Failed to download config from S3: {e}")
    return result_path


def read_config_executor(config_path: str, run_path: str) -> Tuple[str, str]:
    """Return (executor, local_config_path). Downloads from S3 if needed."""
    s3_conf = ensure_s3_conf()
    if config_path.startswith("s3://"):
        if not s3_conf:
            exit_with_error(
                "S3 credentials are required for s3 config path (S3AK/S3SK/S3URL)"
            )
        try:
            loca_path = os.path.join(run_path, "config")
            config_path = download_from_s3(config_path, loca_path, s3_conf)
        except Exception as e:
            exit_with_error(f"Failed to download config from S3: {e}")

    suffix = os.path.splitext(config_path)[1].lower()
    executor = None
    try:
        if suffix in (".yml", ".yaml"):
            import yaml  # type: ignore

            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            executor = (cfg.get("executor") or "ray").lower()
        elif suffix == ".json":
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            executor = (cfg.get("executor") or "ray").lower()
    except FileNotFoundError:
        exit_with_error(f"Config not found: {config_path}")
    except Exception as e:
        logger.warning(f"Failed to parse config {config_path}: {e}")

    if not executor:
        executor = "ray"
    return executor.lower(), config_path


def download_and_extract_package(pkg_path: str, dest_dir: str) -> str:
    """Download (if s3) and extract the package into dest_dir/package, return extracted_dir."""
    s3_conf = ensure_s3_conf()
    local_pkg = pkg_path
    if pkg_path.startswith("s3://"):
        if not s3_conf:
            exit_with_error(
                "S3 credentials are required for s3 package path (S3AK/S3SK/S3URL)"
            )
        try:
            local_pkg = download_from_s3(pkg_path, dest_dir, s3_conf)
        except Exception as e:
            exit_with_error(f"Failed to download package from S3: {e}")

    if not os.path.exists(local_pkg):
        exit_with_error(f"Package not found: {local_pkg}")

    extract_dir = os.path.join(dest_dir, "udf")
    os.makedirs(extract_dir, exist_ok=True)

    # Try shutil.unpack_archive which supports zip, tar, gztar, bztar, xztar
    try:
        shutil.unpack_archive(local_pkg, extract_dir)
    except Exception:
        # fallback to zipfile
        try:
            import zipfile

            with zipfile.ZipFile(local_pkg) as z:
                z.extractall(extract_dir)
        except Exception as e:
            exit_with_error(f"Failed to extract package {local_pkg}: {e}")

    return extract_dir


# -------------------- Ray Cluster Flow --------------------
def start_ray_and_submit(
    config_path: str, world_size: int, master_addr: str, workspace_run: str
):
    try:
        from ray.job_submission import JobStatus, JobSubmissionClient  # type: ignore  # lazy import
    except Exception as e:
        exit_with_error(f"Ray client not available: {e}")

    jobid = extract_jobid(master_addr)
    start_ray_head(jobid, world_size, workspace_run)
    # copy_config_for_log(jobid, config_path)
    wait_for_ray_workers(world_size)
    asyncio.run(submit_ray_job(config_path, workspace_run))


def extract_jobid(master_addr: str) -> str:
    m = re.search(r"job-([0-9a-f-]+)(?=-master)", master_addr)
    return m.group(1) if m else "unknown"


def start_ray_head(jobid: str, world_size: int, workspace_run: str, port: int = 6379):
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
                "--disable-usage-stats",
                # f"--temp-dir={workspace_run}/ray_run/"
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Failed to start Ray head: {e}")
    logger.info("Ray head started.")


def copy_config_for_log(jobid: str, config_path: str):
    log_dir = os.environ.get("RAY_LOG_DIR", f"/tmp/data-engine/process_log/{jobid}")
    os.makedirs(log_dir, exist_ok=True)
    try:
        shutil.copy2(config_path, log_dir)
    except Exception:
        logger.warning("Failed to copy config to log dir; proceeding.")


def wait_for_ray_workers(world_size: int):
    logger.info("Waiting for worker nodes to join...")
    timeout_sec = int(os.environ.get("RAY_WAIT_TIMEOUT_SEC", "600"))
    start_ts = time.time()
    sleep_s = 1.0
    last_report = 0
    while True:
        try:
            # Primary: ray list nodes
            info = subprocess.check_output(
                ["ray", "list", "nodes", "--format", "json"], text=True
            )
            nodes = json.loads(info)
            alive_nodes = [n for n in nodes if n.get("state") == "ALIVE"]
            logger.info(f"nodes: {nodes}")
            # logging.info(f"alive_nodes: {alive_nodes}")
            if len(alive_nodes) >= world_size:
                break
            now = time.time()
            if now - last_report > 10:
                logger.info(f"Ray alive nodes: {len(alive_nodes)}/{world_size}")
                last_report = now
        except Exception as e:
            # Tolerate transient errors and keep retrying until timeout
            logger.warning(f"Checking Ray nodes failed: {e}")
        if time.time() - start_ts > timeout_sec:
            exit_with_error(f"Timed out waiting for Ray workers after {timeout_sec}s")
        time.sleep(sleep_s)
        sleep_s = min(sleep_s * 1.2, 5.0)
    logger.info("All Ray nodes ready.")


async def submit_ray_job(config_path: str, workspace_run: str):
    """Submit Ray job and stream logs with tail_job_logs until finished."""
    from ray.job_submission import JobStatus, JobSubmissionClient

    endpoint = (
        os.environ.get("RAY_DASHBOARD_ADDRESS")
        or os.environ.get("RAY_JOB_SUBMISSION_ADDRESS")
        or "http://127.0.0.1:8265"
    )
    client = JobSubmissionClient(endpoint)

    # 1) 构造 entrypoint
    try:
        suffix = os.path.splitext(config_path)[1].lower()
        if suffix in (".yml", ".yaml", ".json"):
            entry = f"python {root_dir}/tool/launcher.py {config_path}"
        else:
            entry = f"python {config_path}"
        job_id = client.submit_job(entrypoint=entry)
    except Exception as e:
        exit_with_error(f"Failed to submit Ray job: {e}")

    logger.info(f"Job submitted. ID: {job_id}")

    # 2) 日志流任务
    async def watch_logs():
        buffer = []
        flush_size = 100  # 每100行刷一次
        flush_interval = 1  # 或者每1秒定时刷一次

        try:
            with open(
                os.path.join(workspace_run, "ray_run.log"), "a", buffering=1024 * 1024
            ) as f:
                last_flush = asyncio.get_event_loop().time()
                async for line in client.tail_job_logs(job_id):
                    print(line, end="")
                    buffer.append(line)

                    now = asyncio.get_event_loop().time()
                    if len(buffer) >= flush_size or now - last_flush >= flush_interval:
                        f.writelines(buffer)
                        f.flush()  # 刷到内核缓冲
                        os.fsync(f.fileno())  # 可选：强制写盘
                        buffer.clear()
                        last_flush = now
        except Exception as e:
            logger.error(f"Error streaming logs: {e}")

    # 3) 状态监控任务
    async def watch_status():
        while True:
            try:
                info = client.get_job_info(job_id)
                status = info.status
            except Exception as e:
                exit_with_error(f"Failed to get job status: {e}")

            if status in {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.STOPPED}:
                logger.info(f"Job finished with status: {status}")
                if status != JobStatus.SUCCEEDED:
                    exit_with_error(f"Ray job did not succeed. Final status: {status}")
                break
            await asyncio.sleep(5)

    # 4) 并行跑两个任务，直到状态完成
    status_task = asyncio.create_task(watch_status())
    log_task = asyncio.create_task(watch_logs())

    await status_task
    log_task.cancel()
    try:
        await log_task
    except asyncio.CancelledError:
        pass


def join_ray_worker(master_addr: str):
    ray_address = f"{master_addr}:6379"
    try:
        subprocess.run(
            ["ray", "start", "--block", "--address", ray_address], check=True
        )
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Failed to start Ray node: {e}")


# -------------------- Spark (YARN) Flow --------------------
def setup_spark_env():
    os.environ.setdefault("JAVA_HOME", "/usr/lib/jvm/java-1.11.0-openjdk-amd64")
    os.environ.setdefault("HADOOP_HOME", "/opt/hadoop-3.4.0")
    os.environ.setdefault("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3/")
    os.environ.setdefault("PYSPARK_PYTHON", "/opt/conda/bin/python")


def get_spark_custom_params():
    # 参数字典：键为Spark配置名，值为(环境变量名, 默认值)
    spark_params = {
        "spark_driver_memory": "2g",
        "spark_driver_cores": "1",
        "spark_executor_memory": "4g",
        "spark_executor_cores": "2",
        # "spark_executor_instances": "5",
    }

    spark_settings = {}
    for env_name, default_value in spark_params.items():
        # 从环境变量获取值，无则用默认值
        env_value = os.environ.get(env_name, default_value)
        # print(f'--1-{env_name} = {env_value} ')
        if env_value and str(env_value).strip() != "0":
            if "memory" in env_name and "g" not in env_value:
                env_value = f"{env_value}g"
        else:
            env_value = default_value
        # print(f'spark self custom settings:{env_name} = {env_value} ')
        spark_settings[env_name.lower().replace("_", ".")] = env_value
    logger.info(f"spark self custom settings:{spark_settings}")
    return spark_settings


def build_spark_confs(workspace_run):
    target_dir = os.path.join(workspace_run, "spark_run")
    master_addr = os.environ.get("MASTER_ADDR", "localhost")
    conf_dir = "/opt/hadoop_config"
    spark_conf_dir = os.path.join(
        os.environ.get("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3"), "conf"
    )

    # eventLog_dir = os.path.join(target_dir, "eventLog")
    for d in [target_dir, conf_dir, spark_conf_dir, 
            #   eventLog_dir
            ]:
        os.makedirs(d, exist_ok=True)

    def write_xml(path, configs, root_tag="configuration"):
        with open(path, "w") as f:
            f.write(f"<{root_tag}>\n")
            for k, v in configs.items():
                f.write("  <property>\n")
                f.write(f"    <name>{k}</name>\n")
                f.write(f"    <value>{v}</value>\n")
                f.write("  </property>\n")
            f.write(f"</{root_tag}>\n")

    # capacity-scheduler.xml
    write_xml(
        os.path.join(conf_dir, "capacity-scheduler.xml"),
        {
            "yarn.scheduler.capacity.root.queues": "default",
            "yarn.scheduler.capacity.root.default.capacity": "100",
            "yarn.scheduler.capacity.root.default.maximum-capacity": "100",
            "yarn.scheduler.capacity.root.default.state": "RUNNING",
            "yarn.scheduler.capacity.root.default.acl_submit_applications": "*",
            "yarn.scheduler.capacity.root.default.acl_administer_queue": "*",
            "yarn.scheduler.capacity.node-locality-delay": "40",
            "yarn.scheduler.capacity.resource-calculator": "org.apache.hadoop.yarn.util.resource.DefaultResourceCalculator",
        },
    )

    # core-site.xml, yarn-site.xml, mapred-site.xml
    write_xml(
        os.path.join(conf_dir, "core-site.xml"),
        {"fs.defaultFS": f"file://{workspace_run}"},
    )
    write_xml(
        os.path.join(conf_dir, "yarn-site.xml"),
        {
            "yarn.resourcemanager.address": f"{master_addr}:8032",
            "yarn.resourcemanager.scheduler.address": f"{master_addr}:8030",
            "yarn.nodemanager.address": "0.0.0.0:8099",
            "yarn.nodemanager.disk-health-checker.max-disk-utilization-per-disk-percentage": os.environ.get(
                "YARN_NM_DISK_UTILIZATION_PERCENT", "99.0"
            ),
            # 12288,16384,65536
            # 6144 大于spark_executor_memory
            "yarn.scheduler.maximum-allocation-mb": os.environ.get(
                "YARN_SCHEDULER_MAX_ALLOCATION_MB",
                os.environ.get("YARN_NODEMANAGER_MEMORY_MB", "65536"),
            ),
            "yarn.nodemanager.resource.memory-mb": os.environ.get(
                "YARN_NODEMANAGER_MEMORY_MB", "65536"
            ),
            "yarn.nodemanager.resource.cpu-vcores": os.environ.get(
                "YARN.NODEMANAGER.RESOURCE.CPU-VCORES", "16"
            ),
            "yarn.scheduler.maximum-allocation-vcores": os.environ.get(
                "YARN.SCHEDULER.MAXIMUM-ALLOCATION-VCORES", "16"
            ),
        },
    )
    write_xml(
        os.path.join(conf_dir, "mapred-site.xml"),
        {
            "mapreduce.framework.name": "yarn",
            "mapreduce.jobhistory.address": f"{master_addr}:10020",
        },
    )

    # spark-defaults.conf
    spark_defaults = {
        "spark.master": "yarn",
        "spark.submit.deployMode": "cluster",
        "spark.yarn.queue": os.environ.get("YARN_QUEUE", "default"),
        "spark.yarn.stagingDir": f"{target_dir}/.sparkStaging",
        "spark.eventLog.dir": f"{target_dir}/eventLog",
        # "spark.history.fs.logDirectory": f"{target_dir}/eventLog",
        # "spark.eventLog.enabled": "true",
        # Dynamic allocation (shuffle tracking avoids requiring external shuffle service)
        "spark.dynamicAllocation.enabled": "true",
        "spark.dynamicAllocation.shuffleTracking.enabled": "true",
        # 1
        "spark.dynamicAllocation.minExecutors": os.environ.get(
            "SPARK_DYN_MIN_EXECUTORS", "1"
        ),
        "spark.dynamicAllocation.maxExecutors": os.environ.get(
            "SPARK_DYN_MAX_EXECUTORS", "50"
        ),
        # 1
        "spark.dynamicAllocation.initialExecutors": os.environ.get(
            "SPARK_DYN_INITIAL_EXECUTORS",
            os.environ.get("SPARK_DYN_MIN_EXECUTORS", "1"),
        ),
        # Scale-out triggers and idle timeouts
        "spark.dynamicAllocation.schedulerBacklogTimeout": os.environ.get(
            "SPARK_DYN_SCHED_BACKLOG_TIMEOUT", "1s"
        ),
        "spark.dynamicAllocation.sustainedSchedulerBacklogTimeout": os.environ.get(
            "SPARK_DYN_SUSTAINED_BACKLOG_TIMEOUT", "5s"
        ),
        "spark.dynamicAllocation.executorIdleTimeout": os.environ.get(
            "SPARK_DYN_EXECUTOR_IDLE_TIMEOUT", "60s"
        ),
        "spark.dynamicAllocation.cachedExecutorIdleTimeout": os.environ.get(
            "SPARK_DYN_CACHED_EXECUTOR_IDLE_TIMEOUT", "300s"
        ),
        # #增加默认值
        # "spark.driver.memory": f"{os.environ.get('spark_driver_memory', 2)}g",
        # "spark.driver.cores": os.environ.get("spark_driver_cores", 1),
        # "spark.executor.memory": f"{os.environ.get('spark_executor_memory', 4)}g",
        # "spark.executor.cores": os.environ.get("spark_executor_cores", 2),
        # "spark.executor.instances": os.environ.get("spark.executor.instances", 5),
        # 堆外内存设为 1g（根据实际需求调整，确保 5g +1g =6g ≤ 6144 MB）
        "spark.executor.memoryOverhead": os.environ.get(
            "spark_executor_memoryOverhead", "1g"
        ),
    }

    spark_defaults.update(get_spark_custom_params())
    with open(os.path.join(spark_conf_dir, "spark-defaults.conf"), "w") as f:
        for k, v in spark_defaults.items():
            f.write(f"{k} {v}\n")

    # spark-env.sh
    spark_env = f"""
export HADOOP_CONF_DIR={conf_dir}
export YARN_CONF_DIR={conf_dir}
export SPARK_WORKER_DIR={target_dir}/worker
# export SPARK_LOG_DIR={target_dir}/logs
export JAVA_HOME={os.environ.get('JAVA_HOME','/usr/lib/jvm/java-1.11.0-openjdk-amd64')}
"""
    with open(os.path.join(spark_conf_dir, "spark-env.sh"), "w") as f:
        f.write(spark_env)
    os.chmod(os.path.join(spark_conf_dir, "spark-env.sh"), 0o755)

    # yarn-env.sh
    yarn_env = f"""
export JAVA_HOME={os.environ.get('JAVA_HOME','/usr/lib/jvm/java-1.11.0-openjdk-amd64')}
export HADOOP_LOG_DIR={target_dir}/yarn-logs
export HADOOP_OPTS=\"-Xmx1g\"
"""
    with open(os.path.join(conf_dir, "yarn-env.sh"), "w") as f:
        f.write(yarn_env)
    os.chmod(os.path.join(conf_dir, "yarn-env.sh"), 0o755)

    # log4j.properties
    log4j = """
log4j.rootCategory=INFO, console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yy/MM/dd HH:mm:ss} %p %c{1}: %m%n
"""
    with open(os.path.join(spark_conf_dir, "log4j.properties"), "w") as f:
        f.write(log4j)

    return target_dir, conf_dir


def run_with_logging(cmd, **kwargs):
    """Run command, stream combined stdout/stderr to STDOUT, exit 1 on failure."""
    sys.stdout.write(f"[RUN] {' '.join(cmd)}\n")
    sys.stdout.flush()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        **kwargs,
    )
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
        proc.wait()
    finally:
        if proc.stdout:
            proc.stdout.close()
    if proc.returncode != 0:
        exit_with_error(f"Command failed ({proc.returncode}): {' '.join(cmd)}")
    sys.stdout.write(f"[OK] {' '.join(cmd)}\n")
    sys.stdout.flush()


def start_yarn_services():
    rank = int(os.environ.get("RANK", 0))
    hadoop_home = os.environ.get("HADOOP_HOME", "/opt/hadoop-3.4.0")
    yarn_bin = os.path.join(hadoop_home, "bin", "yarn")
    if not os.path.exists(yarn_bin):
        logger.warning(
            f"yarn binary not found at {yarn_bin}, falling back to 'yarn' in PATH (may conflict with Node.js yarn)"
        )
        yarn_bin = "yarn"
    if rank == 0:
        run_with_logging([yarn_bin, "--daemon", "start", "resourcemanager"])
    run_with_logging([yarn_bin, "--daemon", "start", "nodemanager"])


def start_spark_services():
    rank = int(os.environ.get("RANK", 0))
    spark_home = os.environ.get("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3")
    spark_sbin = os.path.join(spark_home, "sbin", "start-history-server.sh")
    if not os.path.exists(spark_sbin):
        logger.warning(
            f"start-history-server binary not found at {spark_sbin}, falling back to 'spark' in PATH"
        )
        # spark_sbin = "start-history-server"
    if rank == 0:
        run_with_logging([spark_sbin])


def submit_spark_job(config_path: str, all_envs):
    """If config_path is a yaml/json => use launcher.py with config.
    Otherwise assume it's an application script and spark-submit that script.
    """
    spark_home = os.environ.get("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3")
    spark_submit = os.path.join(spark_home, "bin", "spark-submit")
    suffix = os.path.splitext(config_path)[1].lower()
    extra_conf = []
    for key, val in all_envs.items():
        extra_conf.extend(
            [
                "--conf",
                f"spark.yarn.appMasterEnv.{key}={val}",
                "--conf",
                f"spark.executorEnv.{key}={val}",
            ]
        )

    if suffix in (".yml", ".yaml", ".json"):
        app = os.path.join(root_dir, "tool", "launcher.py")
        cmd = [spark_submit] + extra_conf + [app, config_path]
    else:
        # treat config_path as application script
        cmd = [spark_submit] + extra_conf + [config_path]

    # logger.info(f"spark exec submit_spark_job suffix:{suffix},cmd={cmd}")
    sys.stdout.write(f"[RUN] {' '.join(cmd)}\n")
    sys.stdout.flush()

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
        proc.wait()
        if proc.stdout:
            proc.stdout.close()
        if proc.returncode != 0:
            exit_with_error(f"Spark job failed with code {proc.returncode}")
    except Exception as e:
        exit_with_error(f"Failed to submit Spark job: {e}")


# -------------------- NodeManager Keepalive --------------------
def _pgrep(pattern: str) -> bool:
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def is_nodemanager_alive() -> bool:
    # Check by JVM main class name
    return _pgrep("org.apache.hadoop.yarn.server.nodemanager.NodeManager")


def monitor_nodemanager_and_block():
    """Blocks the worker process; if NodeManager dies, exit immediately with non-zero code.

    No automatic restart is attempted by design.
    """
    while True:
        if not is_nodemanager_alive():
            exit_with_error(
                "YARN NodeManager process not found, exiting (no auto-restart)."
            )
        time.sleep(5)


# -------------------- Entry --------------------
def main():
    # Command-line modes:
    # 1) config mode: python tool/start.py <config.(yaml|yml|json)>   (argv len == 2)
    # 2) package mode: python tool/start.py <package.zip> <startup_cmd> (argv len == 3)
    if len(sys.argv) < 2:
        exit_with_error(
            "Usage:\n  python tool/start.py <config.(yaml|yml|json)>\n  python tool/start.py <code.zip|...> <startup_cmd>"
        )
    master_addr = os.environ.get("MASTER_ADDR", "")
    workspace = os.environ.get("WORKSPACE") or os.environ.get(
        "workspace", "/share/project/test"
    )
    if not workspace:
        exit_with_error("workspace environment variable not set")
    job_id = extract_jobid(master_addr)
    workspace_run = os.path.join(workspace, f"data-process-{job_id}")
    all_envs = {"workspace": workspace}
    all_envs["workspace_run"] = workspace_run

    udf_path = os.path.join(workspace_run, "udf")

    python_path_env = os.environ.get("PYTHONPATH", "")
    p_list = []

    if python_path_env:
        p_list.extend(python_path_env.split(":"))
    if root_dir and root_dir not in p_list:
        p_list.insert(0, root_dir)
    # if udf_path and udf_path not in p_list:
    #     p_list.insert(0, udf_path)
    all_envs["PYTHONPATH"] = ":".join([p for p in p_list if p])

    import sys as _sys

    for p in [udf_path, root_dir]:
        if p and p not in _sys.path:
            _sys.path.insert(0, p)
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    rank = int(os.environ.get("RANK", 0))
    logger.info(f"RANK={rank}, WORLD_SIZE={world_size}")

    # logger.info(f"os.environ={os.environ}")

    try:
        import resource  # type: ignore

        resource.setrlimit(resource.RLIMIT_NOFILE, (65535, 65535))
    except Exception:
        pass

    # Resolve mode and config/executable
    local_config_path = None
    executor = (os.environ.get("engine") or os.environ.get("executor") or "ray").lower()
    all_envs["executor"] = executor
    config_arg = sys.argv[1]

    all_envs.update(
        {
            "MODEL_S3_AK": os.environ.get("S3AK", ""),
            "MODEL_S3_SK": os.environ.get("S3SK", ""),
            "MODEL_S3_URL": os.environ.get("S3URL", ""),
            "MODEL_S3_ROOT": "zhiyuan-1q1/models",
            "DE_MODEL_CACHE": "/share/project/models",  # os.path.join(workspace_run, "run_models")
        }
    )
    os.environ.update(all_envs)
    for k, v in os.environ.items():
        if "s3" in k.lower():
            all_envs[k] = v
        elif k in (
            "datasource",
            "datasource_root",
            "engine",
        ):
            all_envs[k] = v
    if rank == 0:
        result_path = download(sys.argv[1], workspace_run)
        if len(sys.argv) == 2:
            local_config_path = result_path
        elif len(sys.argv) == 3:
            if not os.path.exists(result_path):
                exit_with_error(f"Package not found: {result_path}")

            extract_dir = os.path.join(workspace_run, "udf")
            os.makedirs(extract_dir, exist_ok=True)
            # Try shutil.unpack_archive which supports zip, tar, gztar, bztar, xztar
            try:
                shutil.unpack_archive(result_path, extract_dir)
            except Exception:
                # fallback to zipfile
                try:
                    import zipfile

                    with zipfile.ZipFile(result_path) as z:
                        z.extractall(extract_dir)
                except Exception as e:
                    exit_with_error(f"Failed to extract package {result_path}: {e}")
            startup_cmd = sys.argv[2]
            startup_script_path = os.path.join(extract_dir, startup_cmd)
            if not os.path.exists(startup_script_path):
                exit_with_error(
                    f"Startup command not found in package: {startup_script_path}"
                )
            # for submission we treat local_config_path as the script to run
            local_config_path = startup_script_path
        else:
            exit_with_error(
                "Too many arguments. Usage:\n  python tool/start.py <config>\n  python tool/start.py <package> <startup_cmd>"
            )

    logger.info(f"Executor resolved: {executor}")
    if executor == "ray":
        if rank == 0:
            start_ray_and_submit(
                local_config_path, world_size, master_addr, workspace_run
            )
        else:
            join_ray_worker(master_addr)
    elif executor == "spark":
        setup_spark_env()
        target_dir, conf_dir = build_spark_confs(workspace_run)
        # Ensure YARN picks up the generated configuration
        os.environ["HADOOP_CONF_DIR"] = conf_dir
        os.environ["YARN_CONF_DIR"] = conf_dir
        start_yarn_services()
        # start_spark_services()
        logger.info(f"spark execute setup_spark_env: {all_envs}")
        if rank == 0:
            submit_spark_job(local_config_path, all_envs)
        else:
            # Workers keep NodeManager alive; if NM dies, exit 1 (or auto-restart if enabled)
            monitor_nodemanager_and_block()
    else:
        exit_with_error(f"Unsupported executor in config: {executor}")


if __name__ == "__main__":
    main()
    # time.sleep(10000)
