output "instance_public_ip" {
  description = "Public IP address of the NC Plus One EC2 instance"
  value       = aws_instance.nc_plus_one.public_ip
}

output "rds_endpoint" {
  description = "RDS PostgreSQL hostname"
  value       = aws_db_instance.nc_plus_one.address
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.nc_plus_one.port
}