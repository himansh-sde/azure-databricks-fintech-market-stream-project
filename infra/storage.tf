# infra/storage.tf

resource "azurerm_storage_account" "adls" {
  # Storage account names must be globally unique and lowercase
  name                     = "st${var.project_name}${var.environment}${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  
  # CRITICAL: Enables Hierarchical Namespace for Spark/Delta performance
  is_hns_enabled           = true

  tags = {
    Environment = var.environment
  }
}

# Container for raw, incoming JSON trades
resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.adls.id
}

# Container for cleaned, deduplicated trades and VWAP output
resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.adls.id
}

# Container exclusively for Spark Structured Streaming state and offsets
resource "azurerm_storage_data_lake_gen2_filesystem" "checkpoints" {
  name               = "checkpoints"
  storage_account_id = azurerm_storage_account.adls.id
}
