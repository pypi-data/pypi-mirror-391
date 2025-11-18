import logging
import sys


class ColoredStreamHandler(logging.StreamHandler):
    COLORS = {
        'DEBUG': '\033[92m',  # Green
        'INFO': '\033[94m',  # Blue
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


def logger() -> logging.Logger:
    if getattr(sys.stdout, "reconfigure", None):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    logging.root.handlers.clear()
    logging.basicConfig(
        level=logging.INFO,
        format="[GPTDriver] %(asctime)s [%(levelname)s]  %(message)s",
        handlers=[
            ColoredStreamHandler(sys.stdout)
        ],
    )
    return logging.getLogger()
