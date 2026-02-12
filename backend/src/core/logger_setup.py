import logging


def get_logger_config():
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )


