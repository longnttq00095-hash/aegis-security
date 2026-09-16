import platform
import psutil


def get_system_info():
    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
    }


def get_cpu_usage():
    return psutil.cpu_percent(interval=0.5)


def get_ram_usage():
    return psutil.virtual_memory().percent


def get_disk_usage():
    return psutil.disk_usage("/").percent