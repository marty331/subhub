resource "aws_secretsmanager_secret" "sub-secret" {
  for_each                  = toset(var.sub_secrets)
  name                      = "sub-${each.value}"
  recovery_window_in_days   = "30"
  description               = ""
  tags                      = var.tags
}

resource "aws_secretsmanager_secret" "hub-secret" {
  for_each                  = toset(var.hub_secrets)
  name                       = "hub-${each.value}"
  recovery_window_in_days   = "30"
  description               = ""
  tags                      = var.tags
}