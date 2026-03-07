from system_launcher import run_system
from logger_engine import log_info, log_error


def run_radar_cycle():

    log_info("Radar cycle started")

    try:

        run_system()

    except Exception as e:

        log_error(f"Radar cycle error: {str(e)}")

    log_info("Radar cycle finished")
