from bot_status import start_bot, stop_bot, is_running
from system_monitor import system_health


def system_report():

    health = system_health()

    status = "RUNNING" if is_running() else "STOPPED"

    report = f"""
🧭 BOT CONTROL PANEL

Status: {status}

CPU Usage: {health['cpu']}%
Memory Usage: {health['memory']}%
"""

    return report


def start_system():

    start_bot()

    return "Bot started"


def stop_system():

    stop_bot()

    return "Bot stopped"
