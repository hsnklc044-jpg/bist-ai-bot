from logger_engine import log_info


def send_alert(message):

    log_info(f"ALERT: {message}")

    print(message)
