import logging


def log_trace(exception: Exception, error: str=None) -> str:
    import traceback

    if error:
        logging.error(f"{error} , error: {exception}")

    trace_info = traceback.format_exc()
    logging.error("Trace Details:\n%s", traceback.format_exc())

    return trace_info