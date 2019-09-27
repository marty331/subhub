# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import uuid

from shared.cfg import CFG


def format_plan_nickname(product_name: str, plan_interval: str) -> str:
    interval_dict = {
        "day": "daily",
        "week": "weekly",
        "month": "monthly",
        "year": "yearly",
    }

    try:
        formatted_interval = interval_dict[plan_interval]
    except KeyError:
        formatted_interval = plan_interval

    return f"{product_name} ({formatted_interval})".title()


def get_indempotency_key() -> str:
    return uuid.uuid4().hex


def event_uppercase(logger, method_name, event_dict):
    event_dict["event"] = event_dict["event"].upper()
    return event_dict


dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(message)s %(lineno)d %(pathname)s %(levelname)-8s %(threadName)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {"json": {"class": "logging.StreamHandler", "formatter": "json"}},
    "loggers": {
        "": {"handlers": ["json"], "level": CFG.LOG_LEVEL},
        "werkzeug": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "pytest": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "pynamodb": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "botocore": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "urllib3": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "connexion": {"level": "ERROR", "handlers": ["json"], "propagate": False},
        "connexion.decorators.validation": {
            "level": CFG.LOG_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
        "openapi_spec_validator": {
            "level": CFG.LOG_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
    },
}
