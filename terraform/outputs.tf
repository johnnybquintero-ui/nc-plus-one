output "instance_public_ip" {
  description = "Public IP address of the NC Plus One EC2 instance"
  value       = aws_instance.nc_plus_one.public_ip
}