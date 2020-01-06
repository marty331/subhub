# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

output "hub_lambda_memory" {
  value = "${lookup(var.HUB_LAMBDA_MEMORY, var.DEPLOYED_ENV)}"
}

output "sub_lambda_memory" {
  value = "${lookup(var.SUB_LAMBDA_MEMORY, var.DEPLOYED_ENV)}"
}

output "deployed_at" {
  value = formatdate("YYYYMMDDhhmmss", timestamp())
}
