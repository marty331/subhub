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
    expect = dict(
        DEPLOYED_BY=CFG.DEPLOYED_BY,
        DEPLOYED_ENV=CFG.DEPLOYED_ENV,
        DEPLOYED_WHEN=CFG.DEPLOYED_WHEN,
    )
    app = create_app()
    client = app.app.test_client()
    client.testing = True
    result = client.get("/v1/sub/deployed")
    assert result.status_code == 200
    actual = jsonify(result.get_data().decode("utf-8"))
    expect.pop("DEPLOYED_WHEN")
    actual.pop("DEPLOYED_WHEN")
    assert expect == actual
