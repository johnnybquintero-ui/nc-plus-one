resource "aws_instance" "nc_plus_one" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = "nc_plus_one_dev"

  vpc_security_group_ids = [aws_security_group.nc_plus_one.id]

  tags = {
    Name = "nc-plus-one-dev"
  }
}

