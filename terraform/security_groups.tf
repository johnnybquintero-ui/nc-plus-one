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