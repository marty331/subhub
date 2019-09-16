# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from sub.shared.cfg import CFG
from sub.shared.deployed import get_deployed


def test_get_deployed():
    """
    test get_deployed
    """
    deployed = dict(
        DEPLOYED_BY=CFG.DEPLOYED_BY,
        DEPLOYED_ENV=CFG.DEPLOYED_ENV,
        DEPLOYED_WHEN=CFG.DEPLOYED_WHEN,
    )
    current_deployed = get_deployed()
    assert current_deployed[0]["DEPLOYED_BY"] == deployed["DEPLOYED_BY"]