# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import requests
from requests import Response

from typing import Dict, Tuple, Any

from hub.routes.abstract import AbstractRoute
from shared.cfg import CFG
from shared.log import get_logger

logger = get_logger()


class SalesforceRoute(AbstractRoute):
    def route(self) -> int:
        if isinstance(self.payload, dict):
            route_payload = self.payload
        else:
            route_payload = json.loads(self.payload)
        basket_url = CFG.SALESFORCE_BASKET_URI + CFG.BASKET_API_KEY
        request_post = requests.post(basket_url, json=route_payload)
        self.report_route(route_payload, "salesforce")
        logger.info(
            "sending to salesforce", payload=self.payload, request_post=request_post
        )
        return request_post.status_code
