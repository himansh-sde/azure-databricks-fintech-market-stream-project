# infra/main.tf

# Generate a random suffix to ensure globally unique storage account names
resource "random_string" "suffix" {
  length  = 5
  special = false
  upper   = false
}

# The main resource group container
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location
  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
