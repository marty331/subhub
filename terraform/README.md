# Terraform

## Up and Running

1. Bootstrap dependencies
2. Initialize Terraform
3. Inspect the Terraform plan
4. Apply the changes

## Bootstrapping

## Initialize Terraform

First, boostrap the dependencies according to:
1. [global/s3](./global/s3/README.md)
2. [global/dynamodb](./global/dynamodb/README.md)

Next initialize Terraform with the following command

```
terraform init -backend-config=backend.hcl
```

## Inspect the Terraform Plan

```
terraform plan
```

## Apply the Changes

```
terraform apply
```

## Author(s)

Stewart Henderson
