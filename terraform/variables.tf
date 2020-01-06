# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

variable "aws_region" {
  type        = "string"
  default     = "us-west-2"
  description = "the region where to provision the stack."
}

######################################
# Secrets
######################################

variable "stripe_api_key" {
  type        = "string"
  description = "The region where to provision the stack."
}

variable "support_api_key" {
  type        = "string"
  description = "The support API key.."
}

variable "payment_api_key" {
  type        = "string"
  description = "The payment API key."
}


######################################
# DynamoDB Configuration
######################################

variable "USERS_TABLE_READ_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "USERS_TABLE_WRITE_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "DELETED_USERS_TABLE_READ_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "DELETED_USERS_TABLE_WRITE_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "EVENTS_TABLE_READ_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "EVENTS_TABLE_WRITE_CAPACITY" {
  type        = "string"
  description = "AWS DynamoDB read capacity setting for the Users table."
  default     = "5"
}

variable "DEPLOYED_ENV" {
  type    = "string"
  default = "dev"
}

variable "USER_TABLE" {
  type    = "string"
  default = "NOT_SET_USER_TABLE"
}

variable "DELETED_USER_TABLE" {
  type    = "string"
  default = "NOT_SET_DELETED_USER_TABLE"
}

variable "EVENT_TABLE" {
  type    = "string"
  default = "NOT_SET_EVENT_TABLE"
}

######################################
# SUB Configuration
######################################

variable "SUB_LAMBDA_PYTHON_RUNTIME" {
  type    = "string"
  default = "python3.7"
}

variable "SUB_LAMBDA_TIMEOUT" {
  type        = "string"
  description = "Sub application, AWS Lambda function timeout"
  default     = "10"
}

variable "SUB_LAMBDA_MEMORY" {
  type        = "map"
  description = "Sub application, AWS Lambda function memory"
  default = {
    dev       = "128"
    fab       = "128"
    prod-test = "512"
    prod      = "512"
  }
}

variable "SUB_LAMBDA_RESERVED_CONCURRENT_EXECUTIONS" {
  type        = "map"
  description = "Hub application, AWS Lambda function reserved concurrent executions"
  default = {
    dev       = "5"
    fab       = "5"
    prod-test = "5"
    prod      = "5"
  }
}

######################################
# HUB Configuration
######################################

variable "HUB_LAMBDA_PYTHON_RUNTIME" {
  type    = "string"
  default = "python3.7"
}

variable "HUB_LAMBDA_TIMEOUT" {
  type        = "string"
  description = "Hub application, AWS Lambda function timeout"
  default     = "10"
}

variable "HUB_LAMBDA_MEMORY" {
  type        = "map"
  description = "Hub application, AWS Lambda function memory"
  default = {
    dev       = "128"
    fab       = "128"
    prod-test = "512"
    prod      = "512"
  }
}

variable "HUB_LAMBDA_RESERVED_CONCURRENT_EXECUTIONS" {
  type        = "map"
  description = "Hub application, AWS Lambda function reserved concurrent executions"
  default = {
    dev       = "5"
    fab       = "5"
    prod-test = "5"
    prod      = "5"
  }
}

# AWS Tags
# The tagging guidelines can be found at
#   https://mana.mozilla.org/wiki/pages/viewpage.action?spaceKey=SRE&title=Tagging
variable "tags" {
  type = "map"
  default = {
    name          = "subhub"
    environment   = ""
    cost-center   = "1440"
    project-name  = "subhub"
    project-desc  = "subhub"
    project-email = "subhub@mozilla.com"
    deployed-env  = ""
    # TODO(low): populate with Terraform version from .terraform-version
    deploy-method = "terraform"
    sources       = "test"
  }
}

variable "default_environment_variables" {
  type = object({
    variables = map(string)
  })
  default = {
    variables = {
      LOG_LEVEL                             = "INFO"
      REPO_URL                              = "https://github.com/mozilla/subhub"
      DEPLOYED_BY                           = "Terraform"
      NEW_RELIC_ACCOUNT_ID                  = ""
      NEW_RELIC_TRUSTED_ACCOUNT_ID          = ""
      NEW_RELIC_SERVERLESS_MODE_ENABLED     = ""
      NEW_RELIC_DISTRIBUTED_TRACING_ENABLED = ""
    }
  }
}

variable "sub_environment_variables" {
  type        = "map"
  description = "Environment variables for the sub lambda function"
  default = {
    variables = {
      USER_TABLE         = ""
      DELETED_USER_TABLE = ""
      PAYMENT_API_KEY    = "payment_api_key"
      TOPIC_ARN_KEY      = ""
      SUPPORT_API_KEY    = ""
    }
  }
}

variable "hub_environment_variables" {
  type        = "map"
  description = "Environment variables for the hub lambda function"
  default = {
    variables = {
      HUB_API_KEY = ""
    }
  }
}
