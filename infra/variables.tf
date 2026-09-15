variable "project_name" {
  type        = string
  default     = "marketstream"
  description = "Base name used for resource naming"
}

variable "location" {
  type        = string
  default     = "eastus"
  description = "Azure Region for all resources"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment (dev/stage/prod)"
}
