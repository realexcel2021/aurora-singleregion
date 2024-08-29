variable "platform_name" {  
}

variable "vpc_cidr_block" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "vpc_id_secondary" {
  type = string
}

variable "db_subnet_group_name" {
  type = string
}

variable "db_subnet_group_name_secondary" {
  type = string
}

variable "region1" {
  type = string
}

variable "region2" {
  type = string
}

variable "database_username_master" {
  type = string
}