import logging
import sys


class Logger:
    _initialised = False

    def __new__(cls, name: str | None = None):
        if not cls._initialised:
            cls._initialise()
            cls._initialised = True
        return logging.getLogger(name)

    @classmethod
    def _initialise(self):
        logging.basicConfig(
            filename="app.log",
            filemode="a",
            format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        )
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
        )
        logger.addHandler(handler)
