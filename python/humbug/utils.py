import os
import types
import sys


def get_cpu_metrics():
    cpu_metrics = {}

    import psutil

    cpu_metrics["cpu_count"] = psutil.cpu_count()
    cpu_metrics["cpu_count_logical"] = psutil.cpu_count(logical=True)
    cpu_metrics["cpu_count_physical"] = psutil.cpu_count(logical=False)
    cpu_metrics["cpu_percent"] = psutil.cpu_percent()
    cpu_metrics["cpu_percent_per_core"] = psutil.cpu_percent(percpu=True)
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    cpu_metrics["cpu_load_by_process"] = current_process.cpu_percent()
    return cpu_metrics


def get_gpu_metrics():
    gpu_metrics = {}

    import GPUtil

    gpus = GPUtil.getGPUs()
    for gpu_unit in gpus:
        gpu_id = gpu_unit.id
        gpu_metrics[f"gpu_{gpu_id}_uuid"] = gpu_unit.uuid
        gpu_metrics[f"gpu_{gpu_id}_load"] = gpu_unit.load
        gpu_metrics[f"gpu_{gpu_id}_memory_util_%"] = gpu_unit.memoryUtil
        gpu_metrics[f"gpu_{gpu_id}_memory_total_MB"] = gpu_unit.memoryTotal
        gpu_metrics[f"gpu_{gpu_id}_memory_used_MB"] = gpu_unit.memoryUsed
        gpu_metrics[f"gpu_{gpu_id}_memory_free_MB"] = gpu_unit.memoryFree
        gpu_metrics[f"gpu_{gpu_id}_driver"] = gpu_unit.driver
        gpu_metrics[f"gpu_{gpu_id}_name"] = gpu_unit.name
        gpu_metrics[f"gpu_{gpu_id}_serial"] = gpu_unit.serial
        gpu_metrics[f"gpu_{gpu_id}_display_mode"] = gpu_unit.display_mode
        gpu_metrics[f"gpu_{gpu_id}_display_active"] = gpu_unit.display_active
        gpu_metrics[f"gpu_{gpu_id}_temperature_C"] = gpu_unit.temperature
    gpu_metrics["gpu_count"] = len(gpus)
    return gpu_metrics


def get_memory_metrics():
    memory_metrics = {}

    import psutil

    system_memory = psutil.virtual_memory()
    memory_metrics["total_MB"] = round(system_memory.total / 1024 / 1024, 2)
    memory_metrics["available_MB"] = round(system_memory.available / 1024 / 1024, 2)
    memory_metrics["percent_%"] = system_memory.percent
    memory_metrics["used_MB"] = round(system_memory.used / 1024 / 1024, 2)
    memory_metrics["free_MB"] = round(system_memory.free / 1024 / 1024, 2)
    swap = psutil.swap_memory()
    memory_metrics["swap_total_MB"] = round(swap.total / 1024 / 1024, 2)
    memory_metrics["swap_used_MB"] = round(swap.used / 1024 / 1024, 2)
    memory_metrics["swap_free_MB"] = round(swap.free / 1024 / 1024, 2)
    memory_metrics["swap_percent_%"] = swap.percent
    return memory_metrics


def get_disk_metrics():
    disk_metrics = {}

    import psutil

    for disk_partition in psutil.disk_partitions():
        disk_usage = psutil.disk_usage(disk_partition.mountpoint)
        disk_metrics[str(disk_partition.mountpoint)] = {}
        disk_metrics[str(disk_partition.mountpoint)]["total_MB"] = round(
            disk_usage.total / 1024 / 1024, 2
        )  # in MB
        disk_metrics[str(disk_partition.mountpoint)]["used_MB"] = round(
            disk_usage.used / 1024 / 1024, 2
        )  # in MB
        disk_metrics[str(disk_partition.mountpoint)]["free_MB"] = round(
            disk_usage.free / 1024 / 1024, 2
        )  # in MB
        disk_metrics[str(disk_partition.mountpoint)]["percent_%"] = disk_usage.percent

    disk_io = psutil.disk_io_counters()
    disk_metrics["read_count"] = disk_io.read_count
    disk_metrics["write_count"] = disk_io.write_count
    disk_metrics["read_MB"] = round(disk_io.read_bytes / 1024 / 1024, 2)  # in MB
    disk_metrics["write_MB"] = round(disk_io.write_bytes / 1024 / 1024, 2)  # in MB
    disk_metrics["read_time_s"] = disk_io.read_time / 1000  # in seconds
    disk_metrics["write_time_s"] = disk_io.write_time / 1000  # in seconds
    disk_metrics["read_merged_count"] = disk_io.read_merged_count
    disk_metrics["write_merged_count"] = disk_io.write_merged_count
    disk_metrics["busy_time_s"] = round(disk_io.busy_time, 2) / 1000  # in seconds
    return disk_metrics


def get_network_metrics():
    network_metrics = {}

    import psutil

    network_io = psutil.net_io_counters()
    network_metrics["MB_sent"] = round(network_io.bytes_sent / 1024 / 1024, 2)  # in MB
    network_metrics["MB_recv"] = round(network_io.bytes_recv / 1024 / 1024, 2)  # in MB
    network_metrics["packets_sent"] = network_io.packets_sent
    network_metrics["packets_recv"] = network_io.packets_recv
    network_metrics["errin"] = network_io.errin
    network_metrics["errout"] = network_io.errout
    network_metrics["dropin"] = network_io.dropin
    network_metrics["dropout"] = network_io.dropout

    return network_metrics


def get_open_files_metrics():
    files_metrics = {}

    import psutil

    open_files = psutil.Process().open_files()
    files_metrics["total"] = len(open_files)

    return files_metrics


def get_thread_metrics():
    threads_metrics = {}

    import psutil

    threads = psutil.Process().threads()
    threads_metrics["total"] = len(threads)

    return threads_metrics


def get_processes_metrics():
    process_metrics = {}

    import psutil

    # get all processes memory usage

    processes = psutil.process_iter()

    # Iterate through each process and get its CPU and memory utilization
    for process in processes:
        cpu_percent = process.cpu_percent()
        mem_info = process.memory_info()
        if process.name() not in process_metrics:
            process_metrics[f"{process.name()}"] = {
                "cpu_percent": cpu_percent,
                "memory_MB": round(mem_info.rss / 1024 / 1024, 2),  # in MB
                "amount_of_processes": 1,
            }
        else:
            process_metrics[f"{process.name()}"]["cpu_percent"] += cpu_percent
            process_metrics[f"{process.name()}"]["memory_MB"] += round(
                mem_info.rss / 1024 / 1024, 2
            )
            process_metrics[f"{process.name()}"]["amount_of_processes"] += 1

    return process_metrics
