# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# https://www.terraform.io/docs/providers/random/r/id.html
resource "random_id" "sub_bucket_name" {
  prefix      = "${var.DEPLOYED_ENV}-sub"
  byte_length = 8
}

resource "aws_s3_bucket" "sub_packages" {
  bucket = random_id.sub_bucket_name.hex
  acl    = "private"
}

resource "random_id" "hub_bucket_name" {
  prefix      = "${var.DEPLOYED_ENV}-hub"
  byte_length = 8
}

resource "aws_s3_bucket" "hub_packages" {
  bucket = random_id.hub_bucket_name.hex
  acl    = "private"
}
