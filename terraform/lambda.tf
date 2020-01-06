# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# NOTE: Local tags for deploying.  These could be specific to your Terraform
# workspace for development, feature toggling, etc.
locals {
  default_tags = {}
}

# https://registry.terraform.io/modules/raymondbutcher/lambda-builder/aws/0.0.6
module "hub_lambda" {
  source               = "git::https://github.com/raymondbutcher/terraform-aws-lambda-builder.git?ref=v0.0.6"
  function_name        = format("%s-%s-hub", var.DEPLOYED_ENV, formatdate("YYYYMMDDhhmmss", timestamp()))
  description          = "The HUB, AWS Lambda"
  handler              = "hub.hubhandler"
  runtime              = "${var.HUB_LAMBDA_PYTHON_RUNTIME}"
  s3_bucket            = aws_s3_bucket.hub_packages.id
  timeout              = "${var.HUB_LAMBDA_TIMEOUT}"
  build_mode           = "LAMBDA"
  source_dir           = "${path.module}/src"
  publish              = true
  role_cloudwatch_logs = true
  tags                 = "${merge(local.default_tags, var.tags)}"
  memory_size          = "${var.HUB_LAMBDA_MEMORY["${var.DEPLOYED_ENV}"]}"
  environment = merge(
    var.default_environment_variables,
    var.hub_environment_variables,
    map(
    "STRIPE_API_KEY", var.stripe_api_key)
  )
}

# https://registry.terraform.io/modules/raymondbutcher/lambda-builder/aws/0.0.6
module "sub_lambda" {
  source               = "git::https://github.com/raymondbutcher/terraform-aws-lambda-builder.git?ref=v0.0.6"
  function_name        = format("%s-%s-sub", var.DEPLOYED_ENV, formatdate("YYYYMMDDhhmmss", timestamp()))
  description          = "The SUB, AWS Lambda"
  handler              = "sub.subhandler"
  runtime              = "${var.SUB_LAMBDA_PYTHON_RUNTIME}"
  s3_bucket            = aws_s3_bucket.sub_packages.id
  timeout              = "${var.SUB_LAMBDA_TIMEOUT}"
  build_mode           = "LAMBDA"
  source_dir           = "${path.module}/src"
  publish              = true
  role_cloudwatch_logs = true
  tags                 = "${merge(local.default_tags, var.tags)}"
  memory_size          = "${var.SUB_LAMBDA_MEMORY["${var.DEPLOYED_ENV}"]}"
  environment = merge(
    var.default_environment_variables,
    var.sub_environment_variables,
    map(
    "STRIPE_API_KEY", var.stripe_api_key)
  )
}
