# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import json
import logging
import boto3
import uuid
from gzip import decompress, compress
from base64 import b64decode, b64encode

NR_TOPIC = os.environ["NR_TOPIC"]
PT_LAMBDA_TOPIC = os.environ["PT_LAMBDA_TOPIC"]
PT_API_TOPIC = os.environ["PT_API_TOPIC"]
MONITORING_TOPIC = os.environ["MONITORING_TOPIC"]
KINESIS_STREAM = os.environ["KINESIS_STREAM"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bare_message = dict({"awslogs": {"data": ""}})
newrelic_json = dict()
papertrail_json = dict()

session = boto3.Session(region_name="us-west-2")
sns_client = session.client("sns")
kinesis_client = session.client("kinesis")


def lambda_handler(event, context):
    logger.info("Starting Python Logger")
    logger.debug("Raw Event:")
    logger.debug(json.dumps(event))
    logger.debug(f"Context: {vars(context)}")

    message = decode_json(event)

    logger.debug(f"Found {len(message['logEvents'])} events here")
    logger.debug("Decoded JSON in raw event")
    logger.debug(message)

    try:
        if "API_Gateway" in message["logGroup"]:
            # These might have shifted to the log groups below
            publish_topic(PT_API_TOPIC, event)
            publish_kinesis(event)
        elif "/aws/lambda/" in message["logGroup"]:
            proc_messages(message)
        elif "/aws/api-gateway" in message["logGroup"]:
            # These are just web traffic logs
            publish_topic(PT_LAMBDA_TOPIC, event)
            publish_kinesis(event)
        else:
            logger.error("We're a total alien entry, disregarding")
            return
    except Exception as e:
        logger.error(f"Log Type ERROR: {e.args[0]}")


def publish_topic(topic, event):
    """
    Send our event payload off to SNS
    :param topic: SNS Topic
    :param event: Lambda Event
    :return: SNS Submission Response
    """
    try:
        response = sns_client.publish(TopicArn=topic, Message=json.dumps(event))
    except Exception as e:
        logger.error(f"Unable to publish to {topic}. ERROR:{e.args[0]}")
    else:
        logger.info(f"Published to {topic}")

    logger.info(response)
    return


def publish_kinesis(event):
    """
    Send events to Firefox Security kinesis stream
    :param event: standard AWS-encoded json payload
    :return: Kinesis response
    """
    partition_key = str(uuid.uuid4())
    try:
        response = kinesis_client.put_record(
            StreamName=KINESIS_STREAM,
            Data=json.dumps(event),
            PartitionKey=partition_key,
        )
    except Exception as e:
        logger.error(
            f"Unable to submit to kinesis stream '{KINESIS_STREAM}' ERROR:{e.args[0]}"
        )
    else:
        logger.info(f"Submitted to kinesis stream '{KINESIS_STREAM}'")

    logger.info(response)
    return


def decode_json(json_input):
    message = b64decode(json_input["awslogs"]["data"])
    message = json.loads(decompress(message).decode("utf-8"))

    return message


def encode_json(json_input):
    message = b64encode(compress(bytes(json.dumps(json_input), "utf-8"))).decode()

    return message


def proc_messages(json_input):
    """
    Process decoded message['awslogs']['data'] message and split up
    New Relic and all others to Papertrail
    """

    output = bare_message
    nr_list = []
    pt_list = []
    for item in json_input["logEvents"]:
        logger.debug(json.dumps(item))
        if "NR_LAMBDA_MONITORING" in item["message"]:
            nr_list.append(item)
        else:
            pt_list.append(item)

        # We want to get notifications for these timeouts
        if "Task timed out" in item["message"]:
            publish_topic(
                MONITORING_TOPIC,
                json_input["logGroup"].split("/")[3] + " " + item["message"],
            )

    logger.info(f"Total Messages: {len(json_input['logEvents'])}")
    json_input["logEvents"] = nr_list
    logger.info(f"New Relic Messages: {len(nr_list)}")

    # Don't post empty message sets
    if len(nr_list) > 0:
        logger.debug(f"Processed NR Messages: {json.dumps(json_input)}")
        output["awslogs"]["data"] = encode_json(json_input)
        publish_topic(NR_TOPIC, output)

    json_input["logEvents"] = pt_list
    logger.info(f"Papertrail Messages: {len(pt_list)}")

    if len(pt_list) > 0:
        logger.debug(f"Processed PT Messages: {json.dumps(json_input)}")
        output["awslogs"]["data"] = encode_json(json_input)
        publish_topic(PT_LAMBDA_TOPIC, output)
        publish_kinesis(output)
