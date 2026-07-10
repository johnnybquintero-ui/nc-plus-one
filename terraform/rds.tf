resource "aws_db_instance" "nc_plus_one" {
  identifier = "nc-plus-one-db"

  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 20
  storage_type        = "gp2"
  db_name             = "nc_plus_one"
  username            = var.db_username
  password            = var.db_password
  port                = 5432
  publicly_accessible = false
  skip_final_snapshot = true
  multi_az            = false

  vpc_security_group_ids = [
    aws_security_group.nc_plus_one_rds.id
  ]

  tags = {
    Name = "nc-plus-one-db"
  }
}