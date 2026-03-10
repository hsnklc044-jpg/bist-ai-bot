import psutil


def system_health():

    cpu = psutil.cpu_percent()

    memory = psutil.virtual_memory().percent

    return {
        "cpu": cpu,
        "memory": memory
    }
