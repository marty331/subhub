# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.



module "stripe_api_key_secret" {
  source  = "rhythmictech/secretsmanager-secret/aws"
  version = "0.0.5"
  name    = format("%s-%s-stripe-api-key-secret", var.DEPLOYED_ENV, formatdate("YYYYMMDDhhmmss", timestamp()))
  value   = "${var.stripe_api_key}"
  tags    = var.tags
}

module "support_api_key_secret" {
  source  = "rhythmictech/secretsmanager-secret/aws"
  version = "0.0.5"
  name    = format("%s-%s-support-api-key-secret", var.DEPLOYED_ENV, formatdate("YYYYMMDDhhmmss", timestamp()))
  value   = "${var.support_api_key}"
  tags    = var.tags
}

module "payment_api_key_secret" {
  source  = "rhythmictech/secretsmanager-secret/aws"
  version = "0.0.5"
  name    = format("%s-%s-payment-api-key-secret", var.DEPLOYED_ENV, formatdate("YYYYMMDDhhmmss", timestamp()))
  value   = "${var.payment_api_key}"
  tags    = var.tags
}
