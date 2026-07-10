variable "db_username" {
  description = "RDS administrator username"
  type        = string
}

variable "db_password" {
  description = "RDS administrator password"
  type        = string
  sensitive   = true
}