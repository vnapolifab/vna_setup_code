import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)s]: %(message)s",
    level=logging.INFO,
    filename="log_file.log"
)

logger = logging.getLogger("logger")
