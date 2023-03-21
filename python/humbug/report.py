"""
This module implements all Humbug methods related to generating reports and publishing them to
Bugout knowledge bases.
"""
import atexit
import concurrent.futures
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import json

import logging
import os
import pkg_resources
import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Optional
import uuid

import requests

from .consent import HumbugConsent
from .system_information import (
    SystemInformation,
    generate as generate_system_information,
)


DEFAULT_URL = "https://spire.bugout.dev"


class BugoutUnexpectedStatusResponse(Exception):
    """
    Raised when Bugout server response return incorrect status.
    """


@dataclass
class Report:
    title: str
    content: str
    tags: List[str] = field(default_factory=list)


class Modes(Enum):
    DEFAULT = 0
    SYNCHRONOUS = 1


class HumbugReporter:
    def __init__(
        self,
        name: str,
        consent: HumbugConsent,
        client_id: Optional[str] = None,
        session_id: Optional[str] = None,
        system_information: Optional[SystemInformation] = None,
        bugout_token: Optional[str] = None,
        timeout_seconds: int = 10,
        mode: Modes = Modes.DEFAULT,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        blacklist_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        if url is None:
            url = DEFAULT_URL
        self.url = url.rstrip("/")
        self.name = name
        self.consent = consent
        self.client_id = client_id
        if session_id is not None:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())
        if system_information is None:
            system_information = generate_system_information()
        self.system_information = system_information
        self.bugout_token = bugout_token
        self.timeout_seconds = timeout_seconds

        self.report_futures: List[concurrent.futures.Future] = []
        atexit.register(self.wait)

        self.executor: Optional[concurrent.futures.Executor] = None
        if mode == Modes.DEFAULT:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="humbug_reporter"
            )

        self.is_excepthook_set = False
        self.is_loggerhook_set = False

        self.tags: List[str] = []
        if tags is not None:
            self.tags = tags

        self.blacklist_fn = blacklist_fn

    def wait(self) -> None:
        concurrent.futures.wait(
            self.report_futures, timeout=float(self.timeout_seconds)
        )
        if self.executor is not None:
            self.executor.shutdown()

    def system_tags(self) -> List[str]:
        tags = [
            "humbug",
            "source:{}".format(self.name),
            "os:{}".format(self.system_information.os),
            "arch:{}".format(self.system_information.machine),
            "python:{}".format(self.system_information.python_version_major),
            "python:{}.{}".format(
                self.system_information.python_version_major,
                self.system_information.python_version_minor,
            ),
            "python:{}".format(self.system_information.python_version),
            "session:{}".format(self.session_id),
        ]
        if self.client_id is not None:
            tags.append("client:{}".format(self.client_id))

        return tags

    def _post_body(self, report: Report) -> Dict[str, Any]:
        return {
            "title": report.title,
            "content": report.content,
            "tags": report.tags + self.tags,
        }

    def publish(self, report: Report, wait: bool = False) -> None:
        if not self.consent.check():
            return
        if self.bugout_token is None:
            return

        json = self._post_body(report)
        headers = {
            "Authorization": "Bearer {}".format(self.bugout_token),
        }
        url = "{}/humbug/reports".format(self.url)

        try:
            report.tags = list(set(report.tags))
            if wait or self.executor is None:
                requests.post(
                    url=url, headers=headers, json=json, timeout=self.timeout_seconds
                )
            else:
                report_future = self.executor.submit(
                    requests.post,
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=self.timeout_seconds,
                )
                self.report_futures.append(report_future)
        except Exception:
            pass

    def custom_report(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Generates (and optionally publishes) a custom report in which the title, tags, and content
        are defined by the caller of this method.
        """
        if tags is None:
            tags = []
        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def system_report(
        self, tags: Optional[List[str]] = None, publish: bool = True, wait: bool = False
    ) -> Report:
        title = "{}: System information".format(self.name)
        content = """### User timestamp
```
{user_time}
```

### OS
```
{os}
```

Release: `{os_release}`

### Processor
```
{machine}
```

### Python
```
{python_version}
```""".format(
            user_time=int(time.time()),
            os=self.system_information.os,
            os_release=self.system_information.os_release,
            machine=self.system_information.machine,
            python_version=self.system_information.python_version,
        )
        report = Report(title=title, content=content, tags=self.system_tags())
        if tags is not None:
            report.tags.extend(tags)
        report.tags.append("type:system")

        if publish:
            self.publish(report, wait=wait)

        return report

    def error_report(
        self,
        error: Exception,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        title = "{} - {}".format(self.name, type(error).__name__)
        error_content = """### User timestamp
```
{user_time}
```

### Exception summary
```
{error_summary}
```

### Traceback
```
{error_traceback}
```""".format(
            user_time=int(time.time()),
            error_summary=repr(error),
            error_traceback="".join(
                traceback.format_exception(
                    etype=type(error),
                    value=error,
                    tb=error.__traceback__,
                )
            ),
        )
        if tags is None:
            tags = []

        tags.extend(["type:error", "error:{}".format(error.__class__.__name__)])
        try:
            tags.append(
                "error_full:{}.{}".format(error.__module__, error.__class__.__name__),
            )
        except Exception:
            pass
        tags.extend(self.system_tags())

        report = Report(title=title, content=error_content, tags=tags)

        if publish:
            self.publish(report, wait=wait)

        return report

    def env_report(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Creates and optionally publishes a report containing the environment variables defined in
        the current process.
        """
        if title is None:
            title = "Environment variables"
        if tags is None:
            tags = []
        tags.append("type:env")

        env_vars = ["{}={}".format(key, value) for key, value in os.environ.items()]
        content = "```\n{}\n```".format("\n".join(env_vars))

        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def packages_report(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Creates and optionally publishes a report containing the packages (and versions of those
        packages) available in the current Python process.
        """
        if title is None:
            title = "Available packages"
        if tags is None:
            tags = []
        tags.append("type:dependencies")

        available_packages = [
            str(package_info) for package_info in pkg_resources.working_set
        ]
        content = "```\n{}\n```".format("\n".join(available_packages))
        report = Report(title, content, tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def compound_report(
        self,
        reports: List[Report],
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        if tags is None:
            tags = []
        for component in reports:
            tags.extend(component.tags)

        if title is None:
            title = "Composite report"

        content = "\n\n- - -\n\n".join(component.content for component in reports)

        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def logging_report(
        self,
        record: logging.LogRecord,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        title = "{} - Logging error - {}".format(self.name, record.module)
        error_content = """### User timestamp
```
{user_time}
```

### Module name
```
{module_name}
```

### Error message
```
{error_message}
```""".format(
            user_time=int(time.time()),
            module_name=record.module,
            error_message=record.getMessage(),
        )
        if tags is None:
            tags = []
        tags.append("type:logging")
        tags.extend(self.system_tags())

        report = Report(title=title, content=error_content, tags=tags)

        if publish:
            self.publish(report, wait=wait)

        return report

    def feature_report(
        self,
        feature_name: str,
        parameters: Dict[str, Any],
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
        apply_blacklist: bool = True,
    ) -> Report:
        title = "Feature used: {name}".format(name=feature_name)

        if apply_blacklist and self.blacklist_fn is not None:
            parameters = self.blacklist_fn(parameters)

        parameters_content = "\n".join(
            [
                "- `{parameter_name}` = `{parameter_value}`".format(
                    parameter_name=key, parameter_value=value
                )
                for key, value in parameters.items()
            ]
        )

        content = """### User timestamp
```
{user_time}
```

### Information

Feature: {name}

{parameters_content}
""".format(
            user_time=int(time.time()),
            name=feature_name,
            parameters_content=parameters_content,
        )

        if tags is None:
            tags = []
        tags.append("type:feature")
        tags.append("feature:{}".format(feature_name))
        tags.extend(self.system_tags())
        tags.extend(
            ["parameter:{}={}".format(key, value) for key, value in parameters.items()]
        )

        report = Report(title=title, content=content, tags=tags)

        if publish:
            self.publish(report, wait=wait)

        return report

    def record_call(
        self,
        callable: Callable,
    ) -> Callable:
        @wraps(callable)
        def wrapped_callable(*args, **kwargs):
            parameters = {**kwargs}
            for i, arg in enumerate(args):
                parameters["arg.{}".format(i)] = arg

            self.feature_report(callable.__name__, parameters)

            return callable(*args, **kwargs)

        return wrapped_callable

    def record_errors(
        self,
        callable: Callable,
    ) -> Callable:
        @wraps(callable)
        def wrapped_callable(*args, **kwargs):
            result = None
            try:
                result = callable(*args, **kwargs)
            except Exception as err:
                self.error_report(err, tags=["site:{}".format(callable.__name__)])
                raise err
            return result

        return wrapped_callable

    def setup_loggerhook(
        self,
        level: int,
        tags: Optional[List[str]] = None,
        publish: bool = True,
    ) -> None:
        if not self.is_loggerhook_set:
            old_factory = logging.getLogRecordFactory()

            def record_factory(*args, **kwargs):
                record = old_factory(*args, **kwargs)
                if record.levelno >= level:
                    self.logging_report(record=record, tags=tags, publish=publish)
                return record

            logging.setLogRecordFactory(record_factory)

            self.is_loggerhook_set = True

    def setup_excepthook(
        self, tags: Optional[List[str]] = None, publish: bool = True
    ) -> None:
        """
        Adds error_report with python Exceptions.
        Only one excepthook will be added to stack, no matter how many
        times you call this method.

        Docs: https://docs.python.org/3/library/sys.html#sys.excepthook
        """
        if not self.is_excepthook_set:
            original_excepthook = sys.excepthook

            def _hook(exception_type, exception_instance, traceback):
                self.error_report(error=exception_instance, tags=tags, publish=publish)
                original_excepthook(exception_type, exception_instance, traceback)

            sys.excepthook = _hook

            self.is_excepthook_set = True

    def setup_notebook_excepthook(self, tags: Optional[List[str]] = None) -> None:
        """
        Excepthook for ipython, works with jupiter notebook.
        """
        ipython_shell = get_ipython()  # type: ignore
        old_showtraceback = ipython_shell.showtraceback

        def showtraceback(*args, **kwargs):
            _, exc_instance, _ = sys.exc_info()
            self.error_report(exc_instance, tags=tags, publish=True)
            old_showtraceback(*args, **kwargs)

        ipython_shell.showtraceback = showtraceback
        self.setup_excepthook(publish=True, tags=tags)

    def metrics_report(self) -> Report:

        title = "Metrics report"

        metrics: Dict[str,Any]  = {}

        cpu = True
        gpu = True
        memory = True
        disk = True
        network = True
        open_files_flag = True
        num_threads_flag = True
        processes_flag = True

        psutil_available = True
        gputil_available = True

        if cpu:

            try:
                import psutil
            except ImportError:
                psutil_available = False

            metrics_cpu = {}

            if psutil_available:
                metrics_cpu["cpu_count"] = psutil.cpu_count()
                metrics_cpu["cpu_count_logical"] = psutil.cpu_count(logical=True)
                metrics_cpu["cpu_count_physical"] = psutil.cpu_count(logical=False)
                metrics_cpu["cpu_percent"] = psutil.cpu_percent()
                metrics_cpu["cpu_percent_per_core"] = psutil.cpu_percent(percpu=True)
                # metrics_cpu["cpu_times"] = psutil.cpu_times()
                # metrics_cpu["cpu_times_percent"] = psutil.cpu_times_percent()
                # metrics_cpu["cpu_times_percent_per_core"] = psutil.cpu_times_percent(
                #     percpu=True
                # )
                # metrics_cpu["cpu_stats"] = psutil.cpu_stats()
                # metrics_cpu["cpu_freq_Mhz"] = psutil.cpu_freq()
                # metrics_cpu["cpu_freq_per_core_Mhz"] = psutil.cpu_freq(percpu=True)
                # cpu_load by process

                # Get the PID of the current process
                current_pid = os.getpid()

                # Use psutil to get more information about the current process
                current_process = psutil.Process(current_pid)

                metrics_cpu["cpu_load_by_process"] = current_process.cpu_percent()
            
            metrics["cpu"] = metrics_cpu


        if gpu:
            try:
                import GPUtil
            except ImportError:
                gputil_available = False
            
            if gputil_available:

                gpus = GPUtil.getGPUs()

                gpu_metrics = {}

                for gpu_unit in gpus:
                    gpu_metrics["gpu_count"] = len(gpus)
                    gpu_id = gpu_unit.id
                    gpu_uuid = gpu_unit.uuid
                    gpu_load = gpu_unit.load
                    gpu_memory_util = gpu_unit.memoryUtil
                    gpu_memory_total = gpu_unit.memoryTotal
                    gpu_memory_used = gpu_unit.memoryUsed 
                    gpu_memory_free = gpu_unit.memoryFree 
                    gpu_driver = gpu_unit.driver
                    gpu_name = gpu_unit.name
                    gpu_serial = gpu_unit.serial
                    gpu_display_mode = gpu_unit.display_mode
                    gpu_display_active = gpu_unit.display_active
                    gpu_temperature = gpu_unit.temperature

                    gpu_metrics[f"gpu_{gpu_id}_uuid"] = gpu_uuid
                    gpu_metrics[f"gpu_{gpu_id}_load"] = gpu_load
                    gpu_metrics[f"gpu_{gpu_id}_memory_util_%"] = gpu_memory_util
                    gpu_metrics[f"gpu_{gpu_id}_memory_total_MB"] = gpu_memory_total
                    gpu_metrics[f"gpu_{gpu_id}_memory_used_MB"] = gpu_memory_used
                    gpu_metrics[f"gpu_{gpu_id}_memory_free_MB"] = gpu_memory_free
                    gpu_metrics[f"gpu_{gpu_id}_driver"] = gpu_driver
                    gpu_metrics[f"gpu_{gpu_id}_name"] = gpu_name
                    gpu_metrics[f"gpu_{gpu_id}_serial"] = gpu_serial
                    gpu_metrics[f"gpu_{gpu_id}_display_mode"] = gpu_display_mode
                    gpu_metrics[f"gpu_{gpu_id}_display_active"] = gpu_display_active
                    gpu_metrics[f"gpu_{gpu_id}_temperature_C"] = gpu_temperature

                metrics["gpu"] = gpu_metrics

        if memory:

            if 'psutil' not in sys.modules:
                try:
                    import psutil
                except ImportError:
                    psutil_available = False

            if psutil_available:

                metrics["memory"] =  {}

                system_memory = psutil.virtual_memory()
                metrics["memory"]["total_MB"] = round(system_memory.total / 1024 / 1024, 2) # in MB
                metrics["memory"]["available_MB"] = round(system_memory.available / 1024 / 1024, 2) # in MB
                metrics["memory"]["percent_%"] = system_memory.percent
                metrics["memory"]["used_MB"] = round(system_memory.used / 1024 / 1024, 2) # in MB
                metrics["memory"]["free_MB"] = round(system_memory.free / 1024 / 1024, 2) # in MB

                swap = psutil.swap_memory()
                metrics["memory"]["swap_total_MB"] = round(swap.total / 1024 / 1024, 2) # in MB
                metrics["memory"]["swap_used_MB"] = round(swap.used / 1024 / 1024, 2) # in MB
                metrics["memory"]["swap_free_MB"] = round(swap.free / 1024 / 1024, 2) # in MB
                metrics["memory"]["swap_percent_%"] = swap.percent
        if disk:
                
                if 'psutil' not in sys.modules:
                    try:
                        import psutil
                    except ImportError:
                        psutil_available = False
    
                if psutil_available:
    
                    metrics["disk"] = {}

                    for disk_partition in psutil.disk_partitions():
                        disk_usage = psutil.disk_usage(disk_partition.mountpoint)
                        metrics["disk"][str(disk_partition.mountpoint)] = {}
                        metrics["disk"][str(disk_partition.mountpoint)]["total_MB"] = round(disk_usage.total / 1024 / 1024, 2) # in MB
                        metrics["disk"][str(disk_partition.mountpoint)]["used_MB"] = round(disk_usage.used / 1024 / 1024, 2) # in MB
                        metrics["disk"][str(disk_partition.mountpoint)]["free_MB"] = round(disk_usage.free / 1024 / 1024, 2) # in MB
                        metrics["disk"][str(disk_partition.mountpoint)]["percent_%"] = disk_usage.percent

    
                    disk_io = psutil.disk_io_counters()
                    metrics["disk"]["read_count"] = disk_io.read_count
                    metrics["disk"]["write_count"] = disk_io.write_count
                    metrics["disk"]["read_MB"] = round(disk_io.read_bytes / 1024 / 1024, 2) # in MB
                    metrics["disk"]["write_MB"] = round(disk_io.write_bytes / 1024 / 1024, 2) # in MB
                    metrics["disk"]["read_time_s"] = disk_io.read_time / 1000 # in seconds
                    metrics["disk"]["write_time_s"] = disk_io.write_time / 1000 # in seconds
                    metrics["disk"]["read_merged_count"] = disk_io.read_merged_count
                    metrics["disk"]["write_merged_count"] = disk_io.write_merged_count
                    metrics["disk"]["busy_time_s"] = round(disk_io.busy_time,2) / 1000 # in seconds

        if network:
                
                if 'psutil' not in sys.modules:
                    try:
                        import psutil
                    except ImportError:
                        psutil_available = False
    
                if psutil_available:
    
                    metrics["network"] = {}
    
                    network_io = psutil.net_io_counters()
                    metrics["network"]["MB_sent"] = round(network_io.bytes_sent / 1024 / 1024, 2) # in MB
                    metrics["network"]["MB_recv"] = round(network_io.bytes_recv / 1024 / 1024, 2) # in MB
                    metrics["network"]["packets_sent"] = network_io.packets_sent
                    metrics["network"]["packets_recv"] = network_io.packets_recv
                    metrics["network"]["errin"] = network_io.errin
                    metrics["network"]["errout"] = network_io.errout
                    metrics["network"]["dropin"] = network_io.dropin
                    metrics["network"]["dropout"] = network_io.dropout

        if open_files_flag:
                    
            if 'psutil' not in sys.modules:
                try:
                    import psutil
                except ImportError:
                    psutil_available = False

            if psutil_available:

                metrics["open_files"] = {}

                open_files = psutil.Process().open_files()
                metrics["open_files"]["total"] = len(open_files)

        if num_threads_flag:
                        
                if 'psutil' not in sys.modules:
                    try:
                        import psutil
                    except ImportError:
                        psutil_available = False
    
                if psutil_available:
    
                    metrics["num_threads"] = {}
    
                    num_threads = psutil.Process().num_threads()
                    metrics["num_threads"]["total"] = num_threads

        if processes_flag:
                            
                if 'psutil' not in sys.modules:
                    try:
                        import psutil
                    except ImportError:
                        psutil_available = False
        
                if psutil_available:
        
                    metrics["processes"] = {}

                    # get all processes memory usage

                    processes = psutil.process_iter()

                    # Iterate through each process and get its CPU and memory utilization
                    for process in processes:
                        cpu_percent = process.cpu_percent()
                        mem_info = process.memory_info()
                        metrics["processes"][f"{process.name()}_{process.pid}"] = {
                            "cpu_percent": cpu_percent,
                            "memory_MB": round(mem_info.rss / 1024 / 1024, 2), # in MB
                        }


        
        report = Report(
            title=title,
            tags=["process_metrics"],
            content=f"```\n{json.dumps(metrics, indent=4, sort_keys=True)}\n```",
        )

        return report



class Reporter(HumbugReporter):
    """
    Deprecated.
    Old class name.
    """

    def __init__(
        self,
        name: str,
        consent: HumbugConsent,
        client_id: Optional[str] = None,
        session_id: Optional[str] = None,
        system_information: Optional[SystemInformation] = None,
        bugout_token: Optional[str] = None,
        bugout_journal_id: Optional[str] = None,
        timeout_seconds: int = 10,
        mode: Modes = Modes.DEFAULT,
    ):
        super().__init__(
            name,
            consent,
            client_id,
            session_id,
            system_information,
            bugout_token,
            timeout_seconds,
            mode,
        )
        self.bugout_journal_id = bugout_journal_id

    def publish(self, report: Report, wait: bool = False) -> None:
        """
        Backwards-compatible publish method in case a Humbug integration has not been set up.

        Using this skips all the benefits you derive from the /humbug/reports endpoint. For
        example:
        1. Deduplication of reports by cache key
        2. Higher rate limit
        """
        if not self.consent.check():
            return

        if self.bugout_token is None:
            return

        if self.bugout_journal_id is None:
            return

        json = {"title": report.title, "content": report.content, "tags": report.tags}
        headers = {
            "Authorization": "Bearer {}".format(self.bugout_token),
        }
        url = "{}/journals/{}/entries".format(self.url, self.bugout_journal_id)

        try:
            report.tags = list(set(report.tags))
            if wait or self.executor is None:
                requests.post(
                    url=url, headers=headers, json=json, timeout=self.timeout_seconds
                )
            else:
                report_future = self.executor.submit(
                    requests.post,
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=self.timeout_seconds,
                )
                self.report_futures.append(report_future)
        except Exception:
            pass
