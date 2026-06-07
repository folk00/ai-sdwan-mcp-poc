terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.40.0, < 6.0.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "name" {
  type    = string
  default = "sdwan-agent-connector"
}

# Public example only. The private lab uses an EC2 + EIP + Caddy pattern
# to provide a stable HTTPS URL while the backend remains local.
resource "aws_eip" "connector" {
  domain = "vpc"
  tags = {
    Name = "${var.name}-eip"
  }
}

output "public_connector_pattern" {
  value = "https://sdwan-agent.${aws_eip.connector.public_ip}.sslip.io"
}
