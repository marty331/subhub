# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from shared.db import (
    HubEvent,
    SubHubDeletedAccount,
    SubHubAccount,
    _create_account_model,
    _create_deleted_account_model,
    _create_hub_model,
)

from shared.dynamodb import dynamodb


def test_create_account_model(dynamodb):
    pass


def test_create_deleted_account_model(dynamodb):
    pass


def test_create_hub_model(dynamodb):
    pass
