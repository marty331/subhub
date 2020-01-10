# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import logging
import os
import boto3
import re
from dateutil.parser import parse
from base64 import b64decode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from email.utils import format_datetime
from dateutil.parser import parse

# Read all the environment variables
SLACK_USER = os.environ["SLACK_USER"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

SLACK_WEBHOOK_URL_ENC = os.environ["SLACK_WEBHOOK_URL"]
# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
SLACK_WEBHOOK_URL = (
    boto3.client("kms")
    .decrypt(CiphertextBlob=b64decode(SLACK_WEBHOOK_URL_ENC))["Plaintext"]
    .decode("utf-8")
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print(context.log_group_name)
    print(context.log_stream_name)
    logger.info("Event: " + str(event))

    # Read message posted on SNS Topic
    message = event["Records"][0]["Sns"]["Message"].encode("utf-8")
    message = re.sub('\n|"', "", message.decode("unicode_escape"))
    message_parts = message.split(" ", 3)

    # ISO dates are a little clunky, we'll convert
    dt = parse(message_parts[1])
    slack_message = (
        f"function: {message_parts[0]}\n"
        f"date: {format_datetime(dt)}\n"
        f"id: {message_parts[2]}\n"
        f"message: {message_parts[3]}\n\n"
    )
    logger.info("Message: " + str(message))
    # Construct a new slack message
    slack_message = {
        "channel": SLACK_CHANNEL,
        "username": SLACK_USER,
        "text": "Application Error",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": slack_message}}
        ],
    }
    # Post message on SLACK_WEBHOOK_URL
    req = Request(
        SLACK_WEBHOOK_URL,
        data=bytes(str(slack_message), encoding="utf-8"),
        headers={"Content-type": "application/json"},
    )
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message["channel"])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
