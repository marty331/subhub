# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json

from sub.app import create_app
from sub.shared.cfg import CFG


def jsonify(string):
    return json.loads(str(string))


def test_version():
    """
    test /version path
    """
    expect = dict(BRANCH=CFG.BRANCH, VERSION=CFG.VERSION, REVISION=CFG.REVISION)
    app = create_app()
    client = app.app.test_client()
    client.testing = True
    result = client.get("/v1/sub/version")
    assert result.status_code == 200
    actual = jsonify(result.get_data().decode("utf-8"))
    assert expect == actual
