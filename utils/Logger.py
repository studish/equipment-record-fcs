#!/usr/bin/env python3

import logging
import logging.config

dictLogConfig = {
    "version": 1,
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "formatter": "myFormatter",
            "filename": "server.log"
        },
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "myFormatter",
        }
    },
    "loggers": {
        "webFramework": {
            "handlers": ["fileHandler", "consoleHandler"],
            "level": "DEBUG",
        },
        "webServer": {
            "handlers": ["fileHandler", "consoleHandler"],
            "level": "DEBUG",
        }
    },
    "formatters": {
        "myFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
}

logging.config.dictConfig(dictLogConfig)

logger = logging.getLogger("webServer")
