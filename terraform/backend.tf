terraform {
  backend "s3" {
    bucket = "nc-plus-one-terraform-state-jq-2026"
    key    = "terraform.tfstate"
    region = "eu-west-2"
  }
}