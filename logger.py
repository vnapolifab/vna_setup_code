import logging  # Import the logging module for creating loggers

# Create a logger with the name 'logger'
logger = logging.getLogger("logger")
# Set the logger's base level to DEBUG, which means all messages from DEBUG level and above will be captured
logger.setLevel(logging.DEBUG)

# Create a file handler to write log messages to a file (log_file.log) and set the logging level to DEBUG
file_handler = logging.FileHandler("log_file.log")
file_handler.setLevel(logging.DEBUG)

# Create a stream handler to print log messages to the console (stdout) and set the logging level to INFO
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create a formatter for the file handler with a custom date-time format and log level
file_handler_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# Set the formatter to the file handler
file_handler.setFormatter(file_handler_formatter)

# Create a simpler formatter for the stream handler with only the log level and message
stream_handler_formatter = logging.Formatter("%(levelname)s: %(message)s")
# Set the formatter to the stream handler
stream_handler.setFormatter(stream_handler_formatter)

# Add both handlers (file and stream) to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# If this script is executed as the main program, log messages at different levels
if __name__ == "__main__":
    logger.debug("This is a debug message")  # Will be written to the log file but not shown in the console
    logger.info("This is an info message")   # Will be written to both the log file and the console
    logger.warning("This is a warning message")  # Will be written to both the log file and the console
    logger.error("This is an error message")    # Will be written to both the log file and the console
    logger.critical("This is a critical message")  # Will be written to both the log file and the console
