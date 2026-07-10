provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = {
      Project      = "nc-plus-one"
      Team         = "Data Engineering"
      DeployedFrom = "Terraform"
      Repository   = "nc-plus-one"
      Environment  = "dev"
    }
  }
}