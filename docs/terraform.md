# Terraform

This project uses Terraform for deployments.  Furthermore
[tfenv](https://github.com/tfutils/tfenv) is used for the management of the version of Terraform
that is used by this project.

## Development

### Install the Providers

`terraform init -upgrade`

# Apply the Changes

`terraform apply -var log_level=$LOG_LEVEL ...`

## References

1. [tfenv](https://github.com/tfutils/tfenv)

## Author(s)

Stewart Henderson
