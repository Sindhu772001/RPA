import logging
import logging.handlers
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class Logger:
    def __init__(self, log_dir='logs', log_file='app.log', max_bytes=10*1024*1024, backup_count=5, rotation_type='size'):
        self.log_dir = log_dir
        self.log_file = log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.rotation_type = rotation_type
        self._ensure_log_dir_exists()
        self.logger = self._setup_logger()

    def _ensure_log_dir_exists(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _setup_logger(self):
        logger = logging.getLogger('app_logger')
        logger.setLevel(logging.DEBUG)

        # Choose handler based on rotation type
        if self.rotation_type == 'size':
            handler = RotatingFileHandler(
                filename=os.path.join(self.log_dir, self.log_file),
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
        elif self.rotation_type == 'time':
            handler = TimedRotatingFileHandler(
                filename=os.path.join(self.log_dir, self.log_file),
                when='midnight',
                interval=1,
                backupCount=self.backup_count
            )
        else:
            raise ValueError("rotation_type must be 'size' or 'time'")

        handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # Adding handlers to the logger
        logger.addHandler(handler)
        logger.addHandler(console_handler)

        return logger

    def get_logger(self):
        return self.logger

# # Example usage
# if __name__ == "__main__":
#     # Initialize the logger with desired rotation type ('size' or 'time')
#     log = Logger(rotation_type='size').get_logger()
#     log.debug('This is a debug message')
#     log.info('This is an info message')
#     log.warning('This is a warning message')
#     log.error('This is an error message')
#     log.critical('This is a critical message')
