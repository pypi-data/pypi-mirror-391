# tool/executors/spark_executor.py
import os
import time
import shutil
from typing import Optional
from data_engine.utils.env_utils import exit_with_error, run_with_logging


def setup_spark_env():
    os.environ.setdefault("JAVA_HOME", "/usr/lib/jvm/java-1.11.0-openjdk-amd64")
    os.environ.setdefault("HADOOP_HOME", "/opt/hadoop-3.4.0")
    os.environ.setdefault("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3/")
    os.environ.setdefault("PYSPARK_PYTHON", "/opt/conda/bin/python")


def get_spark_custom_params():
    # spark自定义参数
    spark_settings = {}
    # for env_name in ['spark.driver.memory','spark.driver.cores','spark.executor.memory','spark.executor.cores']:
    for env_name in [
        "SPARK_DRIVER_MEMORY",
        "SPARK_DRIVER_CORES",
        "SPARK_EXECUTOR_MEMORY",
        "SPARK_EXECUTOR_CORES",
        #  'SPARK_EXECUTOR_INSTANCES'
    ]:
        # env_value = os.environ.get(env_name.upper().replace("_", "."))
        env_value = os.environ.get(env_name.upper())
        # print(f'-- {env_name} = {env_value} ')
        if env_value:
            if not env_value:
                continue
            if "MEMORY" in env_name and "g" not in env_value:
                env_value = f"{env_value}g"
            spark_settings[env_name.lower().replace("_", ".")] = env_value
    return spark_settings


def write_xml(path: str, configs: dict, root_tag: str = "configuration"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"<{root_tag}>\n")
        for k, v in configs.items():
            f.write("  <property>\n")
            f.write(f"    <name>{k}</name>\n")
            f.write(f"    <value>{v}</value>\n")
            f.write("  </property>\n")
        f.write(f"</{root_tag}>\n")


def build_spark_confs(workspace: str, workspace_run: str):
    target_dir = os.path.join(workspace_run, "spark_run")
    master_addr = os.environ.get("MASTER_ADDR", "localhost")
    conf_dir = os.path.join(workspace_run, "hadoop_config")
    spark_conf_dir = os.path.join(
        os.environ.get("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3/"), "conf"
    )
    for d in [target_dir, conf_dir, spark_conf_dir]:
        os.makedirs(d, exist_ok=True)

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
        os.path.join(conf_dir, "core-site.xml"), {"fs.defaultFS": f"file://{workspace}"}
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
            # 16384
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
        "spark.dynamicAllocation.enabled": "true",
        "spark.dynamicAllocation.shuffleTracking.enabled": "true",
        "spark.dynamicAllocation.minExecutors": os.environ.get(
            "SPARK_DYN_MIN_EXECUTORS", "1"
        ),
        "spark.dynamicAllocation.maxExecutors": os.environ.get(
            "SPARK_DYN_MAX_EXECUTORS", "50"
        ),
        "spark.dynamicAllocation.initialExecutors": os.environ.get(
            "SPARK_DYN_INITIAL_EXECUTORS",
            os.environ.get("SPARK_DYN_MIN_EXECUTORS", "1"),
        ),
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
    }
    spark_defaults.update(get_spark_custom_params())
    with open(
        os.path.join(spark_conf_dir, "spark-defaults.conf"), "w", encoding="utf-8"
    ) as f:
        for k, v in spark_defaults.items():
            f.write(f"{k} {v}\n")

    # spark-env.sh
    spark_env = f"""export HADOOP_CONF_DIR={conf_dir}
export YARN_CONF_DIR={conf_dir}
export SPARK_WORKER_DIR={target_dir}/worker
export SPARK_LOG_DIR={target_dir}/logs
export JAVA_HOME={os.environ.get('JAVA_HOME','/usr/lib/jvm/java-1.11.0-openjdk-amd64')}
"""
    with open(os.path.join(spark_conf_dir, "spark-env.sh"), "w", encoding="utf-8") as f:
        f.write(spark_env)
    os.chmod(os.path.join(spark_conf_dir, "spark-env.sh"), 0o755)

    # yarn-env.sh
    yarn_env = f"""export JAVA_HOME={os.environ.get('JAVA_HOME','/usr/lib/jvm/java-1.11.0-openjdk-amd64')}
export HADOOP_LOG_DIR={target_dir}/yarn-logs
export HADOOP_OPTS="-Xmx1g"
"""
    with open(os.path.join(conf_dir, "yarn-env.sh"), "w", encoding="utf-8") as f:
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
    with open(
        os.path.join(spark_conf_dir, "log4j.properties"), "w", encoding="utf-8"
    ) as f:
        f.write(log4j)

    return target_dir, conf_dir


def start_yarn_services():
    rank = int(os.environ.get("RANK", 0))
    hadoop_home = os.environ.get("HADOOP_HOME", "/opt/hadoop-3.4.0")
    yarn_bin = os.path.join(hadoop_home, "bin", "yarn")
    if not os.path.exists(yarn_bin):
        logging.warning(
            f"yarn binary not found at {yarn_bin}, falling back to 'yarn' in PATH"
        )
        yarn_bin = "yarn"
    if rank == 0:
        run_with_logging([yarn_bin, "--daemon", "start", "resourcemanager"])
    run_with_logging([yarn_bin, "--daemon", "start", "nodemanager"])


def submit_spark_job(
    config_path: str,
    root_dir: str,
    package_archive: Optional[str] = None,
    package_startup_cmd: Optional[list] = None,
):
    """
    If package_archive is None: submit launcher.py config (original).
    If package_archive provided: submit package_startup_cmd by using --archives package_archive#udf
    and running udf/<script> as the app.
    package_startup_cmd must start with 'python <script>'.
    """
    spark_bin = os.path.join(
        os.environ.get("SPARK_HOME", "/opt/spark-3.5.6-bin-hadoop3/"),
        "bin",
        "spark-submit",
    )
    if package_archive:
        if not package_startup_cmd or len(package_startup_cmd) < 2:
            exit_with_error(
                "Spark package mode requires startup command like: python <script> [args...]"
            )
        if package_startup_cmd[0] not in ("python", "python3"):
            exit_with_error(
                "Spark package mode only supports Python startup command (python <script>)."
            )
        main_script = package_startup_cmd[1]
        app_path = os.path.join("udf", main_script)
        cmd = [spark_bin, "--archives", f"{package_archive}#udf", app_path] + (
            package_startup_cmd[2:] if len(package_startup_cmd) > 2 else []
        )
        run_with_logging(cmd)
    else:
        app = os.path.join(root_dir, "tool", "launcher.py")
        cmd = [spark_bin, app, config_path]
        run_with_logging(cmd)


def monitor_nodemanager_and_block():
    import subprocess

    def _pgrep(pattern: str) -> bool:
        return (
            subprocess.run(
                ["pgrep", "-f", pattern],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )

    while True:
        if not _pgrep("NodeManager"):
            exit_with_error(
                "YARN NodeManager process not found, exiting (no auto-restart)."
            )
        time.sleep(5)
