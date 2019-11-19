# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest

from pytest_bdd import scenarios, given, when, then, parsers

scenarios("../features/version.feature")

# Given Steps


@given(parsers.parse('a "{application}" deployment'))
def given_a_deployment(app, application):
    pass


# When Steps


@when(parsers.parse('the user gets "{endpoint}"'))
def get(endpoint):
    pass


# Then Steps


@then(parsers.parse('the response code should be "{phrase}"'))
def response_is(phrase):
    pass
