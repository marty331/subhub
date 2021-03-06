# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import json


class MockSqsClient:
    @staticmethod
    def list_queues(QueueNamePrefix=None):
        return {"QueueUrls": ["DevSub"]}

    @staticmethod
    def send_message(QueueUrl=None, MessageBody=None):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


class MockSnsClient:
    @staticmethod
    def publish(
        Message: dict = None, MessageStructure: str = "json", TopicArn: str = None
    ):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


class MockSubhubAccount:
    def subhub_account(self):
        pass


class MockSubhubUser:
    id = "123"
    cust_id = "cust_123"
