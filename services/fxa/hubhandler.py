#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging

# TODO!
# import newrelic.agent
import serverless_wsgi
import structlog

serverless_wsgi.TEXT_MIME_TYPES.append("application/custom+json")

from os.path import join, dirname, realpath
# First some funky path manipulation so that we can work properly in
# the AWS environment
sys.path.insert(0, join(dirname(realpath(__file__)), 'src'))

# TODO!
# newrelic.agent.initialize()

from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.context import Context
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

from hub.app import create_app

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
)

logger = get_logger()

xray_recorder.configure(service="fxa.hub")
patch_all()

hub_app = create_app()
XRayMiddleware(hub_app.app, xray_recorder)

# TODO!
# @newrelic.agent.lambda_handler()
# NOTE: The context object has the following available to it.
#   https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html#python-context-object-props
# NOTE: Available environment passed to the Flask from serverless-wsgi
#   https://github.com/logandk/serverless-wsgi/blob/2911d69a87ae8057110a1dcf0c21288477e07ce1/serverless_wsgi.py#L126
def handle(event, context):
    try:
        logger.info("handling hub event", subhub_event=event, context=context)
        return serverless_wsgi.handle_request(hub_app.app, event, context)
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("exception occurred", subhub_event=event, context=context, error=e)
        # TODO: Add Sentry exception catch here
        raise
