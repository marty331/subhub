# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# TODO(low): create instead of importing
# resource "aws_route53_zone" "main" {
#   name = "${var.primary_zone}"
# }

# resource "aws_route53_zone" "env_zone" {
#   name = "${var.DEPLOYED_ENV}.${var.primary_zone}"
#   tags = var.TAGS
# }

# resource "aws_route53_record" "nameservers" {
#   zone_id = "${aws_route53_zone.main.zone_id}"
#   name    = "${var.DEPLOYED_ENV}.${var.primary_zone}"
#   type    = "NS"
#   ttl     = "30"
#   records = [
#     "${aws_route53_zone.env_zone.name_servers.0}",
#     "${aws_route53_zone.env_zone.name_servers.1}",
#     "${aws_route53_zone.env_zone.name_servers.2}",
#     "${aws_route53_zone.env_zone.name_servers.3}",
#   ]
# }

# resource "aws_acm_certificate" "acm_certification" {
#   domain_name       = "${var.DEPLOYED_ENV}.${var.primary_zone}"
#   validation_method = "DNS"
#   tags = var.TAGS
#   lifecycle {
#     create_before_destroy = true
#   }
# }
