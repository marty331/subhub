# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import boto3
import json

from typing import Dict, Any
from botocore.exceptions import ClientError
from stripe.error import APIConnectionError

from hub.routes.abstract import AbstractRoute
from hub.shared.cfg import CFG
from shared.log import get_logger

logger = get_logger()


class FirefoxRoute(AbstractRoute):
    def route(self) -> Dict[str, Any]:
        try:
            sns_client = boto3.client("sns", region_name=CFG.AWS_REGION)
            response = sns_client.publish(
                TopicArn=CFG.TOPIC_ARN_KEY,
                Message=json.dumps(
                    {"default": self.payload}
                ),  # json.dumps is required by FxA
                MessageStructure="json",
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("message sent to Firefox queue", response=response)
                logger.info("firefox payload", payload=self.payload)
                if isinstance(self.payload, dict):
                    route_payload = self.payload
                else:
                    route_payload = json.loads(self.payload)
                self.report_route(route_payload, "firefox")
                return response
        except ClientError as e:
            logger.error("Firefox error", error=e)
            self.report_route_error(self.payload)
