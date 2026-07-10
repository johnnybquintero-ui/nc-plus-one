resource "aws_security_group" "nc_plus_one" {
  name        = "nc_plus_one_ssh"
  description = "Allow SSH from the developer IP only"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "nc-plus-one-ssh"
  }

  ingress {
    description = "SSH from developer IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["217.155.255.196/32"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "nc_plus_one_http" {
  name        = "nc-plus-one-http"
  description = "Allow public HTTP access to FastAPI"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "FastAPI HTTP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "nc-plus-one-http"
  }
}

resource "aws_security_group" "nc_plus_one_rds" {
  name        = "nc-plus-one-rds"
  description = "Allow PostgreSQL access from the application EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.nc_plus_one.id]
  }

  tags = {
    Name = "nc-plus-one-rds"
  }
}