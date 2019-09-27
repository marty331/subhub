# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

LOGGER = None

def get_logger():
    global LOGGER
    if not LOGGER:
        from structlog import configure, processors, stdlib, threadlocal, get_logger
        from pythonjsonlogger import jsonlogger

        from shared.universal import dict_config, event_uppercase

        logging.config.dictConfig(dict_config)

        configure(
                context_class=threadlocal.wrap_dict(dict),
                logger_factory=stdlib.LoggerFactory(),
                wrapper_class=stdlib.BoundLogger,
                processors=[
                    # Filter only the required log levels into the log output
                    stdlib.filter_by_level,
                    # Adds logger=module_name (e.g __main__)
                    stdlib.add_logger_name,
                    # Uppercase structlog's event name which shouldn't be convoluted with AWS events.
                    event_uppercase,
                    # Allow for string interpolation
                    stdlib.PositionalArgumentsFormatter(),
                    # Render timestamps to ISO 8601
                    processors.TimeStamper(fmt="iso"),
                    # Include the stack dump when stack_info=True
                    processors.StackInfoRenderer(),
                    # Include the application exception when exc_info=True
                    # e.g log.exception() or log.warning(exc_info=True)'s behavior
                    processors.format_exc_info,
                    # Decodes the unicode values in any kv pairs
                    processors.UnicodeDecoder(),
                    # Creates the necessary args, kwargs for log()
                    stdlib.render_to_log_kwargs,
                ],
                cache_logger_on_first_use=True,
            )

        LOGGER = get_logger()
    return LOGGER
