from pipeline_manager import run_pipeline
from logger_engine import log_info


def run_workflow():

    log_info("Workflow started")

    results = run_pipeline()

    log_info("Workflow finished")

    return results
