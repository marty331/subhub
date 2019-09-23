# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json

from sub.app import create_app
from sub.shared.cfg import CFG


def jsonify(string):
    return json.loads(str(string))


def test_plans():
    """
    test /plans path
    """
    expect = [
        {
            "amount": 999,
            "currency": "usd",
            "interval": "month",
            "plan_id": "plan_FiII5wajzrxfrl",
            "plan_name": "Project Guardian (Monthly)",
            "product_id": "prod_FiIHtYW7rZmzlb",
            "product_name": "Project Guardian",
        },
        {
            "amount": 0,
            "currency": "usd",
            "interval": "month",
            "plan_id": "plan_FKMbsUQUfJGv2G",
            "plan_name": "Moz_Sub (Monthly)",
            "product_id": "prod_EtMczoDntN9YEa",
            "product_name": "Moz_Sub",
        },
        {
            "amount": 100,
            "currency": "usd",
            "interval": "day",
            "plan_id": "plan_F4G9jB3x5i6Dpj",
            "plan_name": "Moz_Sub (Daily)",
            "product_id": "prod_EtMczoDntN9YEa",
            "product_name": "Moz_Sub",
        },
        {
            "amount": 10000,
            "currency": "usd",
            "interval": "year",
            "plan_id": "plan_Ex9bCAjGvHv7Rv",
            "plan_name": "Vulpes Vulpes (Yearly)",
            "product_id": "prod_Ex9Z1q5yVydhyk",
            "product_name": "Vulpes Vulpes",
        },
        {
            "amount": 1000,
            "currency": "usd",
            "interval": "month",
            "plan_id": "plan_Ex9azKcjjvGzB5",
            "plan_name": "Vulpes Vulpes (Monthly)",
            "product_id": "prod_Ex9Z1q5yVydhyk",
            "product_name": "Vulpes Vulpes",
        },
        {
            "amount": 6000,
            "currency": "usd",
            "interval": "year",
            "plan_id": "plan_EuPRQDU7BxhfCD",
            "plan_name": "Moz_Sub (Yearly)",
            "product_id": "prod_EtMczoDntN9YEa",
            "product_name": "Moz_Sub",
        },
        {
            "amount": 1000,
            "currency": "usd",
            "interval": "month",
            "plan_id": "plan_EtMcOlFMNWW4nd",
            "plan_name": "Moz_Sub (Monthly)",
            "product_id": "prod_EtMczoDntN9YEa",
            "product_name": "Moz_Sub",
        },
    ]

    app = create_app()
    client = app.app.test_client()
    client.testing = True
    headers = {"Accept": "application/json", "Authorization": CFG.PAYMENT_API_KEY}

    result = client.get("/v1/sub/plans", headers=headers)
    assert result.status_code == 200
    actual = jsonify(result.get_data().decode("utf-8"))
    assert expect == actual
